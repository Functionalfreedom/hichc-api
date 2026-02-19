from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DealData(BaseModel):
    name: str
    price: float
    sde: float
    re_val: float

@app.post("/generate-memo")
async def generate_memo(payload: DealData):
    try:
        # 1. INSTITUTIONAL MATH
        monthly_mgt_load = 10000 
        monthly_sde = payload.sde / 12
        monthly_ebitda = monthly_sde - monthly_mgt_load

        mezz_p = payload.price * 0.60
        vtb_p = payload.price * 0.40
        
        # Debt Service
        m_mezz_int = (mezz_p * 0.08) / 12
        vtb_annual_principal = vtb_p / 10
        m_vtb_pmt = ((vtb_p * 0.06) + vtb_annual_principal) / 12
        m_net = monthly_ebitda - m_mezz_int - m_vtb_pmt

        # Year 3 Exit Metrics (Simplified)
        yr3_val = (payload.sde * 1.10) * (payload.price / payload.sde) if payload.sde > 0 else 0
        kicker = (yr3_val - mezz_p - vtb_p) * 0.10
        moic = ((m_mezz_int * 36) + mezz_p + kicker) / mezz_p if mezz_p > 0 else 0

        # 2. FORMATTING
        s = {
            "name": payload.name.upper(),
            "net": "${:,.0f}".format(m_net),
            "ebitda": "${:,.0f}".format(monthly_ebitda),
            "debt": "-${:,.0f}".format(m_mezz_int + m_vtb_pmt),
            "moic": "{:.2f}x".format(moic),
            "audit": "${:,.0f}".format(payload.price * 0.02)
        }

        memo_html = f"""
<div style="font-family:sans-serif;color:#fff;background:#000;padding:30px;border-radius:12px;border:1px solid #333;max-width:800px;margin:auto;">
    <div style="border-bottom:2px solid #3eb0ef;padding-bottom:15px;margin-bottom:25px;display:flex;justify-content:space-between;align-items:flex-end;">
        <div>
            <div style="color:#3eb0ef;font-size:11px;font-weight:bold;letter-spacing:1.5px;">HICHC | INVESTMENT COMMITTEE</div>
            <h1 style="margin:0;font-size:26px;">{s['name']}</h1>
        </div>
        <div style="text-align:right;">
            <div style="font-size:10px;color:#888;">TARGET MOIC</div>
            <div style="color:#00ff41;font-weight:bold;font-size:14px;">{s['moic']}</div>
        </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:15px;margin-bottom:30px;">
        <div style="background:#111;padding:15px;border:1px solid #222;text-align:center;">
            <div style="font-size:10px;color:#888;margin-bottom:5px;">MONTHLY EBITDA</div>
            <div style="font-size:20px;font-weight:bold;">{s['ebitda']}</div>
        </div>
        <div style="background:#111;padding:15px;border:1px solid #222;text-align:center;">
            <div style="font-size:10px;color:#888;margin-bottom:5px;">DEBT SERVICE</div>
            <div style="font-size:20px;font-weight:bold;color:#ff4141;">{s['debt']}</div>
        </div>
        <div style="background:#111;padding:15px;border:1px solid #222;text-align:center;">
            <div style="font-size:10px;color:#888;margin-bottom:5px;">MONTHLY NET</div>
            <div style="font-size:20px;font-weight:bold;color:#00ff41;">{s['net']}</div>
        </div>
    </div>
    <div style="background:#0a0a0a;padding:25px;border-radius:10px;border:1px solid #222;line-height:1.6;">
        <h3 style="color:#3eb0ef;margin-top:0;font-size:16px;border-bottom:1px solid #222;padding-bottom:10px;">EXECUTIVE INVESTMENT THESIS</h3>
        <p style="font-size:14px;color:#ccc;"><b>Strategic Rationale:</b> Acquisition of industrial asset. Model accounts for <b>$120k/yr DOO load</b> to professionalize operations.</p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:20px 0;">
            <div>
                <h4 style="font-size:12px;color:#888;margin-bottom:8px;">Structure</h4>
                <ul style="font-size:13px;padding-left:18px;margin:0;color:#bbb;">
                    <li>Mezzanine: 60% @ 8%</li>
                    <li>VTB: 40% @ 6%</li>
                </ul>
            </div>
            <div>
                <h4 style="font-size:12px;color:#888;margin-bottom:8px;">Closing Details</h4>
                <ul style="font-size:13px;padding-left:18px;margin:0;color:#bbb;">
                    <li>10-Yr VTB Amort</li>
                    <li>Audit Fee: {s['audit']}</li>
                </ul>
            </div>
        </div>
    </div>
</div>
"""
        return {"memo": memo_html}
    except Exception as e:
        return {"memo": f"Error: {str(e)}"}