from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# region, latency_ms, uptime_pct (from q-vercel-latency.json)
ROWS = [["apac", 204.41, 97.454], ["apac", 227.61, 98.177], ["apac", 162.95, 97.344], ["apac", 169.91, 98.582], ["apac", 201.34, 99.303], ["apac", 207.75, 98.046], ["apac", 138.43, 97.636], ["apac", 166.33, 97.585], ["apac", 170.42, 97.782], ["apac", 231.37, 98.423], ["apac", 116.37, 98.706], ["apac", 203.71, 97.915], ["emea", 203.88, 97.193], ["emea", 196.58, 97.517], ["emea", 120.26, 98.998], ["emea", 165.14, 98.387], ["emea", 121.85, 98.104], ["emea", 182.43, 98.993], ["emea", 197.51, 97.705], ["emea", 236.03, 99.314], ["emea", 128.52, 98.655], ["emea", 139.35, 97.808], ["emea", 150.88, 99.371], ["emea", 179.02, 97.639], ["amer", 210.57, 97.637], ["amer", 124.95, 99.397], ["amer", 212.23, 97.22], ["amer", 194.54, 99.182], ["amer", 177.62, 98.844], ["amer", 118.62, 97.274], ["amer", 214.22, 97.22], ["amer", 160.85, 98.04], ["amer", 141.49, 97.95], ["amer", 166.24, 97.328], ["amer", 172.26, 99.301], ["amer", 131.03, 98.313]]

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class Query(BaseModel):
    regions: List[str]
    threshold_ms: float


def percentile(values, p):
    """Linear-interpolation percentile (same as numpy.percentile default)."""
    s = sorted(values)
    k = (len(s) - 1) * p / 100
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/")
@app.post("/api")
def metrics(q: Query):
    out = {}
    for region in q.regions:
        rows = [r for r in ROWS if r[0] == region]
        if not rows:
            continue
        lat = [r[1] for r in rows]
        up = [r[2] for r in rows]
        out[region] = {
            "avg_latency": sum(lat) / len(lat),
            "p95_latency": percentile(lat, 95),
            "avg_uptime": sum(up) / len(up),
            "breaches": sum(1 for x in lat if x > q.threshold_ms),
        }
    return {"regions": out}
