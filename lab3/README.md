# Lab 3 - Component Modelling & Architectural Pattern Selection

## Project

**Group Travel Expense Simplification Engine**
**SRN:** PES1UG24CS606
**Domain:** Retail, E-Commerce & Finance
**Actors:** Group Traveler, Trip Admin

## Architecture

The project uses a **Layered Architecture implemented as a modular monolith**. The client calls an API and access-control layer, which delegates to trip/expense and settlement components. A trip ledger repository provides transactional persistence, while an FX rate adapter isolates the external daily exchange-rate provider.

The design covers expense capture, trip-member administration, balance viewing, dated currency conversion, and min-transaction settlement. The API checks authentication and trip roles before protected data is accessed. The settlement engine is kept in-process to avoid unnecessary network hops for the specified target of under 100 ms for 50 travelers and 500 expenses; that target still requires benchmarking.

## Deliverables

- `Group_Travel_Expense_Component_Diagram.png` - exported UML component diagram
- `Group_Travel_Expense_Component_Diagram.pdf` - printable diagram
- `Group_Travel_Expense_Component_Diagram.svg` - editable vector source
- `Architecture_Justification.docx` and `.pdf` - one-page architecture choice and required rationale
- `Architecture_Style_Analysis.docx` and `.pdf` - comparison of Layered, Microservices, and Client-Server styles
- `architecture_choice.md` - editable justification text
- `generate_lab3_assets.py` - source generator for the diagram and documents

## Regenerate

From the repository root, run:

```powershell
python .\lab3\generate_lab3_assets.py
```

The generator requires `Pillow`, `python-docx`, `pypdf`, and `reportlab`.
