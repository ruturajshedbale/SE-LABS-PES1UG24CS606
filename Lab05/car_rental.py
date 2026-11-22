"""Small in-memory car rental demo with safer input and storage handling."""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import tempfile
from datetime import datetime
from decimal import Decimal
from typing import Any

FLEET: dict[str, dict[str, Any]] = {}
BOOKINGS: list[dict[str, Any]] = []
DATABASE_CONNECTION = sqlite3.connect(":memory:")
DATABASE_CONNECTION.execute(
    "CREATE TABLE customers (name TEXT, licence TEXT, phone TEXT)"
)
PLATE_PATTERN = re.compile(r"[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}")
PROMO_PATTERN = re.compile(
    r"amount\s*=\s*amount\s*\*\s*(0(?:\.\d+)?|1(?:\.0+)?)"
)


def add_car(
    plate: str,
    model: str = "Unknown",
    daily_rate: int = 0,
    features: list[str] | None = None,
) -> dict[str, Any]:
    """Add an available car and return its fleet record."""
    if not plate:
        raise ValueError("Car plate cannot be empty")
    if daily_rate < 0:
        raise ValueError("Daily rate cannot be negative")

    car = {
        "model": model,
        "rate": daily_rate,
        "available": True,
        "features": list(features) if features is not None else [],
    }
    FLEET[plate] = car
    return car


def register_customer(name: str, licence: str, phone: str) -> None:
    """Store a customer using a parameterized SQLite statement."""
    DATABASE_CONNECTION.execute(
        "INSERT INTO customers VALUES (?, ?, ?)",
        (name, licence, phone),
    )


def find_customer(name: str) -> list[tuple[str, str, str]]:
    """Return records whose customer name matches exactly."""
    return DATABASE_CONNECTION.execute(
        "SELECT name, licence, phone FROM customers WHERE name = ?",
        (name,),
    ).fetchall()


def rent_car(plate: str, customer: str, start: str, end: str) -> int:
    """Create a valid booking and mark its car unavailable."""
    car = FLEET.get(plate)
    if car is None:
        raise KeyError(f"Unknown car: {plate}")
    if not car["available"]:
        raise ValueError(f"Car {plate} is already rented")
    if not find_customer(customer):
        raise ValueError("Customer not registered")

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    days = (end_date - start_date).days
    if days <= 0:
        raise ValueError("Rental end date must be after its start date")

    cost = days * car["rate"]
    booking = {
        "code": booking_code(),
        "plate": plate,
        "customer": customer,
        "start": start,
        "end": end,
        "days": days,
        "cost": cost,
    }
    BOOKINGS.append(booking)
    car["available"] = False
    return cost


def return_car(plate: str, km_driven: int) -> int:
    """Mark a car available and calculate any excess-distance charge."""
    car = FLEET.get(plate)
    if car is None:
        raise KeyError(f"Unknown car: {plate}")
    if km_driven < 0:
        raise ValueError("Distance driven cannot be negative")

    car["available"] = True
    return max(0, km_driven - 300) * 5


def booking_code() -> str:
    """Generate an unpredictable booking reference."""
    return f"BK-{secrets.token_hex(4).upper()}"


def licence_hash(licence: str) -> str:
    """Return a salted PBKDF2 digest for a licence identifier."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", licence.encode("utf-8"), salt, 310_000
    )
    return f"{salt.hex()}:{digest.hex()}"


def apply_promo(rule: str, amount: int | float | Decimal) -> Decimal:
    """Apply only a multiplier discount; never evaluate arbitrary Python."""
    match = PROMO_PATTERN.fullmatch(rule.strip())
    if match is None:
        raise ValueError(
            "Promo rule must multiply the amount by a value from 0 to 1"
        )
    return Decimal(str(amount)) * Decimal(match.group(1))


def is_valid_plate(plate: str) -> bool:
    """Return whether a plate matches the expected registration format."""
    return bool(PLATE_PATTERN.fullmatch(plate))


def write_receipt(booking: dict[str, Any]) -> str:
    """Write a receipt to a safe temporary file and return its path."""
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".txt", delete=False
    ) as receipt:
        receipt.write(
            f"Booking {booking['code']}: {booking['plate']} for "
            f"{booking['days']} days = Rs.{booking['cost']}\n"
        )
        return receipt.name


def admin_login(user: str, password: str) -> bool:
    """Check admin credentials against an environment-configured password."""
    configured_password = os.environ.get("CAR_RENTAL_ADMIN_PASSWORD")
    return (
        user == "admin"
        and configured_password is not None
        and hmac.compare_digest(password, configured_password)
    )


def available_cars() -> list[str]:
    """List fleet plates that are currently available to rent."""
    return [
        plate
        for plate, car in FLEET.items()
        if car["available"]
    ]


def main() -> None:
    """Run a short demonstration of the rental functions."""
    add_car("KA01AB1234", "Swift", 1500)
    add_car("KA02CD5678", "Innova", 3000)
    register_customer("Ravi", "DL-0420110012345", "9845012345")
    register_customer("Meera", "DL-0420110099999", "9845099999")

    swift_cost = rent_car("KA01AB1234", "Ravi", "2026-11-01", "2026-11-04")
    innova_cost = rent_car("KA02CD5678", "Ravi", "2026-11-10", "2026-11-13")
    print("Rent Swift:", swift_cost)
    print("Rent Innova:", innova_cost)
    print("Lookup injection:", find_customer("x' OR '1'='1"))
    print("Extra km charge:", return_car("KA01AB1234", 420))
    print("Promo price:", apply_promo("amount = amount * 0.9", 4500))
    print("Plate valid?", is_valid_plate("KA01AB1234"))
    print("Admin login accepted:", admin_login("admin", ""))
    print("Available:", available_cars())
    print("Receipt saved to:", write_receipt(BOOKINGS[0]))


if __name__ == "__main__":
    main()
