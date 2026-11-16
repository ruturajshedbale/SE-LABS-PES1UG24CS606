# Architecture Selection

We chose **Layered Architecture (modular monolith)** for the **Group Travel Expense Simplification Engine**.

**Reason 1 - One consistent trip ledger.** A single trip-and-expense domain service maintains payers, participants, currency conversion, and traveler balances. The settlement engine works from those normalized balances so each result can be checked against the net-zero invariant.

**Reason 2 - Clear boundaries without distributed-service overhead.** Separate layers handle traveler/admin requests, authorization, expense workflows, settlement, persistence, and exchange-rate integration. This is a better fit than independently deployed microservices for the stated project scope.

**Security advantage.** The API authenticates requests and checks trip membership and the Trip Admin role before allowing protected expense or participant changes. Clients do not access the ledger repository directly; requests pass through the authorized service layer.

**Performance benefit.** The settlement engine runs in the same application deployment and consumes bounded trip data, avoiding an extra network hop for the under-100-ms target (50 travelers and 500 expenses). Indexing and the stated workload still require benchmark validation; this design does not claim measured performance.

The layered design keeps balance and settlement rules testable, supports the required workflows, and leaves a clear integration seam for daily exchange rates.
