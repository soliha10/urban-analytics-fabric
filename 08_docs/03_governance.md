# Governance Policies

## 1. Access control
| Role | Workspace role | Scope |
|---|---|---|
| Data engineer | Contributor | Build and run pipelines, dataflows, notebooks |
| Data owner | Admin | Workspace settings, permissions, capacity |
| City manager | Viewer (+ `CityManager` RLS role, planned) | Full report |
| Borough analyst | Viewer (+ `BoroughAnalyst` RLS role, planned) | Own borough only |
| Public | Publish to web link | `rpt_urban_analytics_public` only, read-only |

- Principle of least privilege: consumers never get Member/Contributor (these bypass RLS).
- Access is granted to Entra ID **groups**, not individuals.
- OpenAQ API key is stored only as a Dataflow parameter, never in notebooks or reports.

## 2. Row-Level Security (optional in scope — designed, not activated)
Designed on `DimBorough`, driven by `gold.SecurityUserBorough`: role definitions in `07_analytics/04_rls_roles.dax`,
steps in `07_analytics/05_rls_guide.md`, mapping table in `05_warehouse/07_create_security.sql`.
Adding a user = inserting one row, no model change. The roles are not created in the deployed model because the
project scope marks RLS as optional and Publish to web does not allow models with RLS.

## 3. Data classification and labels
| Item | Sensitivity label | Reason |
|---|---|---|
| Lakehouses, Warehouse | General | Open public datasets, no PII |
| Semantic model, Report | General | Aggregated data only |
| Public report (Publish to web) | Public | Open datasets only; the security table holds only a placeholder email |

Endorsement: `wh_urban_analytics` and `sm_urban_analytics` → **Certified** after review; others → **Promoted**.

## 4. Data quality rules
| Layer | Rule |
|---|---|
| Silver taxi | Trip inside analysis window, 1–240 min, 0.1–200 miles, fare ≥ 0, total > 0, deduplicated |
| Silver air | NYC bounding box, value ≥ 0, unified units, one value per sensor-hour |
| Silver FX | Rate > 0, one rate per day |
| Silver GDP | Non-null value, one row per country-year |
| Gold FX | Weekend/holiday rates forward-filled from last business day |
| Warehouse | PK/FK constraints declared (NOT ENFORCED) for model integrity |

Every `write_table` call prints the row count, visible in Monitor hub run output.

## 5. Lineage
Fabric Lineage view + Microsoft Purview (see `02_lineage.md`).

## 6. Refresh and retention
| Item | Schedule |
|---|---|
| `pl_master` | Daily 03:00 (UTC+05:00 Toshkent); off while the capacity is paused |
| `df_openaq` (optional) | Hourly |
| Taxi files | Skipped when already present (monthly source) |

- Bronze keeps raw files indefinitely (re-processing source of truth).
- Silver/Gold tables are rebuilt with overwrite; Delta time travel keeps previous versions.
  Run `VACUUM` monthly with 7-day retention to control storage.

## 7. Known limitations
- Air-quality stations are mapped to the nearest borough centroid (approximation).
- Correlation does not imply causation; weather is a confounder not included in this scope.
- OpenAQ coverage varies by station; `sensor_count` and `reading_count` expose data completeness.
