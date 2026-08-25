# PES1UG24CS606 — Group Travel Expense Simplification Engine

## Requirements Table

| Req ID | Type | Description | Priority | Acceptance Criteria | Rationale |
|---|---|---|---|---|---|
| FR-001 | Functional | The system shall compute the optimal debt settlement graph using min-flow algorithms to minimize total peer-to-peer payment transactions. | High | **Pass:** Group balance settles to net zero with minimum payment edges. **Fail:** Sum of debts does not equal sum of credits. | Core functionality for minimizing the number of settlement transactions. |
| FR-002 | Functional | The system shall allow a Group Traveler to record an expense by entering the amount, currency, payer, and participating travelers. | High | **Pass:** A valid expense is saved with amount, currency, payer, and participants. **Fail:** The expense is saved with missing mandatory information. | Expense recording provides the primary input for settlement. |
| FR-003 | Functional | The system shall convert foreign-currency expenses into the selected base currency using the applicable daily exchange rate. | High | **Pass:** The converted amount matches the applicable daily exchange rate calculation. **Fail:** The conversion is incorrect or no valid exchange rate is available. | Supports multi-currency group travel expenses. |
| FR-004 | Functional | The system shall allow a Group Traveler to view their current net balance for the trip. | High | **Pass:** The displayed net balance matches the recorded expenses and applicable splits. **Fail:** The displayed balance is incorrect. | Allows travelers to know how much they owe or are owed. |
| FR-005 | Functional | The system shall allow the Trip Admin to add or remove Group Travelers from a trip. | Medium | **Pass:** The Trip Admin can successfully add or remove travelers. **Fail:** An unauthorized user can modify the traveler list. | Provides controlled management of trip participants. |
| NFR-001 | Nonfunctional | The settlement calculation engine must execute in under 100 ms for groups of up to 50 travelers with 500 expenses. | High | **Pass:** Benchmark testing confirms settlement calculation completes in under 100 ms for the specified load. **Fail:** Execution time is 100 ms or more. | Ensures fast settlement calculations under the specified workload. |
| NFR-002 | Nonfunctional | The system shall restrict access to trip and expense information to authenticated and authorized users. | High | **Pass:** Unauthenticated or unauthorized users are denied access to protected trip and expense data. **Fail:** Protected data is accessible without proper authorization. | Protects private travel and financial information. |

## Project Information

- **Student / SRN:** PES1UG24CS606
- **Project:** Group Travel Expense Simplification Engine
- **Domain:** Retail, E-Commerce & Finance
- **Actors:** Group Traveler, Trip Admin
- **Requirements:** Exactly 5 Functional Requirements and 2 Non-Functional Requirements
