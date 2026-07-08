# Skill: .NET Unit & Integration Testing (xUnit)

Load this skill for all backend (non-Blazor-UI) .NET testing. For Blazor
component testing, use `blazor-testing-bunit.md` instead/in addition.

## Framework defaults

- **xUnit** is the default test framework for .NET unless the repo already
  uses NUnit/MSTest — follow whatever's already there.
- **Moq** or **NSubstitute** for mocking dependencies — follow whichever
  is already used in the repo; don't mix both in the same project.
- **FluentAssertions** for readable assertions, if already a dependency —
  otherwise plain xUnit `Assert.*` is fine.

## Naming & structure

- Test class mirrors the class under test: `OrderServiceTests` for
  `OrderService`.
- Test method name states scenario and expectation:
  `MethodName_Scenario_ExpectedResult`
  (e.g. `CreateOrder_WhenStockIsInsufficient_ThrowsDomainException`).
- Arrange/Act/Assert structure, with blank lines separating the three
  sections for readability.

## Testing MediatR handlers

- Unit test handlers directly (construct the handler with mocked
  dependencies), not through the MediatR pipeline, for fast focused tests.
- Test pipeline behaviors (validation, logging) separately and in
  isolation from individual handlers.

## Testing EF Core code

- Prefer **Testcontainers** (real SQL Server/PostgreSQL in a disposable
  Docker container) for integration tests that exercise actual EF Core
  queries/migrations — the EF Core InMemory provider does not behave
  identically to a real relational database (no real constraints,
  different query translation) and can hide bugs.
- Reserve the InMemory provider for very fast, low-stakes unit tests where
  the SQL semantics genuinely don't matter.

## Testing ASP.NET Core APIs

- Use `WebApplicationFactory<TEntryPoint>` for integration tests that spin
  up the full API in-memory and issue real HTTP requests via
  `HttpClient` — this is the standard approach for testing minimal
  APIs/controllers end-to-end, including middleware and DI wiring.
- Override registered services (e.g. swap the real DbContext for a
  Testcontainers-backed one) via `WithWebHostBuilder` +
  `ConfigureTestServices`.

## Coverage tooling

- `dotnet test --collect:"XPlat Code Coverage"` (Coverlet) is the standard
  way to measure coverage in .NET — report the touched-code coverage
  against the `testingCoverage` config value, per
  `coverage-analysis.md`.
