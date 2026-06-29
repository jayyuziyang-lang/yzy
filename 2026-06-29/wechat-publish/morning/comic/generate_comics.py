"""
Generate Dalio-style SVG comics for 6.29 morning report.
Panel-001: 美伊周末剧震 — 霍尔木兹一日三转 (开火→停火→油价过山车)
Panel-002: 黄金=利率预期资产的终极确认 — 天平博弈
"""
import xml.etree.ElementTree as ET

def make_svg():
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 512" width="768" height="512" font-family="Microsoft YaHei, SimHei, sans-serif">
  <rect width="768" height="512" fill="#FAFBFC"/>
</svg>'''

# ============================================================
# Panel-001: 霍尔木兹一日三转 — 时间线叙事漫画
# ============================================================
panel_001 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 512" width="768" height="512" font-family="Microsoft YaHei, SimHei, sans-serif">
  <rect width="768" height="512" fill="#FAFBFC"/>

  <!-- Title bar -->
  <rect x="24" y="18" width="720" height="42" rx="6" fill="#1A56DB" opacity="0.1"/>
  <text x="384" y="46" text-anchor="middle" font-size="18" font-weight="700" fill="#1A56DB">霍尔木兹一日三转 · 周末48小时地缘过山车</text>

  <!-- Time axis line -->
  <line x1="64" y1="110" x2="704" y2="110" stroke="#475569" stroke-width="3" stroke-linecap="round"/>
  <circle cx="64" cy="110" r="5" fill="#475569"/>
  <circle cx="704" cy="110" r="5" fill="#475569"/>

  <!-- Event 1: 周六 AM — 美军空袭 -->
  <rect x="48" y="130" width="200" height="125" rx="8" fill="#FFF5F5" stroke="#DC2626" stroke-width="2"/>
  <text x="148" y="154" text-anchor="middle" font-size="12" font-weight="700" fill="#DC2626">周六凌晨</text>
  <text x="148" y="175" text-anchor="middle" font-size="15" font-weight="700" fill="#DC2626">美军空袭伊朗</text>
  <text x="148" y="197" text-anchor="middle" font-size="11" fill="#991B1B">报复伊朗攻击商船</text>
  <text x="148" y="218" text-anchor="middle" font-size="11" fill="#991B1B">"Kiku号"油轮遭袭</text>
  <text x="148" y="239" text-anchor="middle" font-size="11" fill="#991B1B">200万桶原油失控</text>
  <!-- explosion icon -->
  <circle cx="148" cy="248" r="16" fill="none" stroke="#DC2626" stroke-width="1.5" opacity="0.3"/>

  <!-- Arrow 1 -->
  <text x="256" y="160" text-anchor="middle" font-size="20" fill="#1A56DB">→</text>
  <text x="256" y="178" text-anchor="middle" font-size="10" fill="#64748B">油价急涨</text>
  <text x="256" y="194" text-anchor="middle" font-size="10" fill="#64748B">WTI→$72+</text>

  <!-- Event 2: 周六 PM — 伊朗报复 -->
  <rect x="280" y="130" width="200" height="125" rx="8" fill="#FFF7ED" stroke="#EA580C" stroke-width="2"/>
  <text x="380" y="154" text-anchor="middle" font-size="12" font-weight="700" fill="#EA580C">周六傍晚</text>
  <text x="380" y="175" text-anchor="middle" font-size="15" font-weight="700" fill="#EA580C">伊朗反击</text>
  <text x="380" y="197" text-anchor="middle" font-size="11" fill="#9A3412">摧毁科威特+巴林</text>
  <text x="380" y="218" text-anchor="middle" font-size="11" fill="#9A3412">8个美军基地</text>
  <text x="380" y="239" text-anchor="middle" font-size="11" fill="#9A3412">谈判单方面取消</text>

  <!-- Arrow 2 -->
  <text x="488" y="160" text-anchor="middle" font-size="20" fill="#1A56DB">→</text>
  <text x="488" y="178" text-anchor="middle" font-size="10" fill="#64748B">恐慌升级</text>
  <text x="488" y="194" text-anchor="middle" font-size="10" fill="#64748B">避险飙升</text>

  <!-- Event 3: 周日 — 停火 -->
  <rect x="516" y="130" width="200" height="125" rx="8" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
  <text x="616" y="154" text-anchor="middle" font-size="12" font-weight="700" fill="#16A34A">周日（Axios）</text>
  <text x="616" y="175" text-anchor="middle" font-size="15" font-weight="700" fill="#16A34A">双方同意停火</text>
  <text x="616" y="197" text-anchor="middle" font-size="11" fill="#14532D">周二多哈重谈</text>
  <text x="616" y="218" text-anchor="middle" font-size="11" fill="#14532D">聚焦霍尔木兹管理</text>
  <text x="616" y="239" text-anchor="middle" font-size="11" fill="#14532D">WTI跌破$70→反弹</text>

  <!-- Oil price roller coaster -->
  <rect x="48" y="280" width="670" height="100" rx="8" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="1.5"/>
  <text x="70" y="304" font-size="13" font-weight="700" fill="#1E40AF">油价过山车</text>

  <!-- Oil price path -->
  <polyline points="80,360 200,310 350,370 500,340 650,350" fill="none" stroke="#1A56DB" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>
  <circle cx="80" cy="360" r="4" fill="#1A56DB"/>
  <circle cx="200" cy="310" r="4" fill="#DC2626"/>
  <circle cx="350" cy="370" r="4" fill="#DC2626"/>
  <circle cx="500" cy="340" r="4" fill="#16A34A"/>
  <circle cx="650" cy="350" r="4" fill="#1A56DB"/>

  <!-- Labels on path -->
  <text x="80" y="382" text-anchor="middle" font-size="10" fill="#64748B">周五 $70.39</text>
  <text x="200" y="298" text-anchor="middle" font-size="10" fill="#DC2626">空袭 $72+</text>
  <text x="350" y="392" text-anchor="middle" font-size="10" fill="#DC2626">伊朗反击</text>
  <text x="520" y="328" text-anchor="middle" font-size="10" fill="#16A34A">停火跌破$70</text>
  <text x="650" y="338" text-anchor="middle" font-size="10" fill="#1A56DB">$69.97</text>

  <!-- Key insight bar -->
  <rect x="48" y="400" width="670" height="48" rx="6" fill="#F0F4FF" stroke="#1A56DB" stroke-width="1.5"/>
  <text x="384" y="422" text-anchor="middle" font-size="14" font-weight="700" fill="#1E40AF">双方都没有全面战争的意愿 — 但海峡脆弱性未改</text>
  <text x="384" y="440" text-anchor="middle" font-size="11" fill="#64748B">48小时"开火→报复→停火" = 2026年最密集的外交反转</text>

  <!-- Brand line -->
  <line x1="24" y1="480" x2="744" y2="480" stroke="#1A56DB" stroke-width="2" opacity="0.3"/>
  <text x="384" y="496" text-anchor="middle" font-size="9" fill="#94A3B8">扬说财经早报 · 2026.06.29</text>
</svg>'''

# ============================================================
# Panel-002: 黄金=利率预期资产 — 天平博弈
# ============================================================
panel_002 = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 768 512" width="768" height="512" font-family="Microsoft YaHei, SimHei, sans-serif">
  <rect width="768" height="512" fill="#FAFBFC"/>

  <!-- Title bar -->
  <rect x="24" y="18" width="720" height="42" rx="6" fill="#D4A017" opacity="0.1"/>
  <text x="384" y="46" text-anchor="middle" font-size="18" font-weight="700" fill="#B8860B">黄金四周连跌的真相：不是避险资产，是利率预期资产</text>

  <!-- Balance scale -->
  <!-- Stand -->
  <rect x="374" y="380" width="20" height="80" rx="3" fill="#475569"/>
  <rect x="340" y="450" width="88" height="14" rx="7" fill="#475569"/>

  <!-- Beam (tilted — right side heavier) -->
  <line x1="120" y1="120" x2="648" y2="200" stroke="#475569" stroke-width="5" stroke-linecap="round"/>
  <!-- Fulcrum -->
  <circle cx="384" cy="160" r="14" fill="#64748B"/>
  <circle cx="384" cy="160" r="8" fill="#94A3B8"/>

  <!-- Left pan — "避险需求" (lighter, higher) -->
  <line x1="180" y1="125" x2="180" y2="165" stroke="#475569" stroke-width="2"/>
  <path d="M120,165 Q180,200 240,165" fill="#FEF2F2" stroke="#DC2626" stroke-width="2"/>
  <text x="180" y="185" text-anchor="middle" font-size="13" font-weight="700" fill="#DC2626">地缘避险</text>
  <text x="180" y="203" text-anchor="middle" font-size="10" fill="#991B1B">伊朗空袭→金价？</text>
  <text x="180" y="219" text-anchor="middle" font-size="10" fill="#991B1B">没有涨</text>

  <!-- Right pan — "利率预期" (heavier, lower) -->
  <line x1="588" y1="195" x2="588" y2="235" stroke="#475569" stroke-width="2"/>
  <path d="M528,235 Q588,270 648,235" fill="#F0FDF4" stroke="#16A34A" stroke-width="2"/>
  <text x="588" y="255" text-anchor="middle" font-size="13" font-weight="700" fill="#16A34A">利率预期</text>
  <text x="588" y="273" text-anchor="middle" font-size="10" fill="#14532D">PCE 3.4%→加息↑</text>
  <text x="588" y="289" text-anchor="middle" font-size="10" fill="#14532D">→金价持续承压</text>

  <!-- Weight labels — showing why right is heavier -->
  <text x="528" y="220" font-size="9" fill="#94A3B8">1kg</text>
  <text x="160" y="150" font-size="9" fill="#94A3B8" transform="rotate(-7, 160, 150)">0.2kg</text>

  <!-- Gold price trajectory -->
  <rect x="48" y="320" width="670" height="68" rx="8" fill="#FFFBEB" stroke="#FDE68A" stroke-width="1.5"/>
  <text x="70" y="344" font-size="13" font-weight="700" fill="#92400E">金价走势：$4,483 → $4,088（四周连跌-9%）</text>

  <!-- Downward arrows -->
  <polyline points="90,375 170,375" stroke="#D4A017" stroke-width="10" stroke-linecap="round"/>
  <polyline points="210,375 290,375" stroke="#D4A017" stroke-width="10" stroke-linecap="round"/>
  <polyline points="330,375 410,375" stroke="#D4A017" stroke-width="10" stroke-linecap="round"/>
  <polyline points="450,375 530,375" stroke="#D4A017" stroke-width="10" stroke-linecap="round"/>

  <text x="130" y="368" text-anchor="middle" font-size="9" fill="#92400E">5月底</text>
  <text x="250" y="368" text-anchor="middle" font-size="9" fill="#92400E">PCE前</text>
  <text x="370" y="368" text-anchor="middle" font-size="9" fill="#92400E">PCE公布</text>
  <text x="490" y="368" text-anchor="middle" font-size="9" fill="#92400E">周末</text>
  <text x="130" y="388" text-anchor="middle" font-size="10" font-weight="700">$4,483</text>
  <text x="370" y="388" text-anchor="middle" font-size="10" font-weight="700">$4,050</text>
  <text x="490" y="388" text-anchor="middle" font-size="10" font-weight="700" fill="#DC2626">$4,088.87</text>

  <!-- Key insight bar -->
  <rect x="48" y="406" width="670" height="48" rx="6" fill="#FFFBEB" stroke="#D4A017" stroke-width="1.5"/>
  <text x="384" y="428" text-anchor="middle" font-size="14" font-weight="700" fill="#92400E">黄金的决定性力量不是地缘风险，是利率预期</text>
  <text x="384" y="446" text-anchor="middle" font-size="11" fill="#92400E">油价跌→通胀预期↓→金价周五反弹1.56% — 这条因果链清晰验证了黄金的"利率预期资产"本质</text>

  <!-- Brand line -->
  <line x1="24" y1="480" x2="744" y2="480" stroke="#D4A017" stroke-width="2" opacity="0.3"/>
  <text x="384" y="496" text-anchor="middle" font-size="9" fill="#94A3B8">扬说财经早报 · 2026.06.29</text>
</svg>'''

# Write both SVGs
with open("panel-001.svg", "w", encoding="utf-8") as f:
    f.write(panel_001)
with open("panel-002.svg", "w", encoding="utf-8") as f:
    f.write(panel_002)

# Validate
for name in ["panel-001.svg", "panel-002.svg"]:
    try:
        ET.parse(name)
        size = len(open(name, encoding="utf-8").read())
        print(f"[OK] {name}: XML valid, {size}B ({size/1024:.1f}KB)")
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
