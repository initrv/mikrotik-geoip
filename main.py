import httpx
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import PlainTextResponse

app = FastAPI(title="MikroTik GeoIP Service")

SOURCE_URL = "https://github.com/ipverse/rir-ip/raw/refs/heads/master/country/{country}/ipv4-aggregated.txt"


@app.get("/")
async def health_check():
    return {"status": "running", "usage": "/geoip/{country_code}"}


@app.get("/geoip/{country_code}", response_class=PlainTextResponse)
async def get_geoip_script(country_code: str):
    country = country_code.lower()
    list_name = f"GeoIP-{country}"
    url = SOURCE_URL.format(country=country)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, follow_redirects=True)

            if resp.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Country code '{country}' not found in upstream source.",
                )

            if resp.status_code not in [200, 302]:
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch data from GitHub.",
                )

            raw_data = resp.text

    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Upstream connection failed.")

    # Check if file is empty
    if not raw_data.strip():
        raise HTTPException(status_code=404, detail="Source file is empty.")

    # Process the lines
    lines = raw_data.splitlines()
    script_lines = []

    # Header info (Log and Remove old list)
    script_lines.append(
        f'/log info "Loading MikroTik-GeoIP-{country} ipv4 address list"'
    )
    script_lines.append(
        f"/ip firewall address-list remove [/ip firewall address-list find list={list_name}]"
    )
    script_lines.append("/ip firewall address-list")

    # Body (Add new addresses)
    count = 0
    for line in lines:
        line = line.strip()
        # Ignore comments and empty lines
        if line and not line.startswith("#"):
            # The :do {} on-error={} syntax ensures the script continues even if an IP is invalid/duplicate
            script_lines.append(
                f":do {{ add address={line} list={list_name} }} on-error={{}}"
            )
            count += 1

    # Join with newlines
    final_script = "\n".join(script_lines)

    # Return as a file download stream (Optional: add headers to force download)
    return Response(
        content=final_script,
        media_type="text/plain",
        headers={
            "Content-Disposition": f'attachment; filename="MikroTik-GeoIP-{country}.rsc"',
            "X-Record-Count": str(count),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
