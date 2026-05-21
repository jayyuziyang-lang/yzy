#!/usr/bin/env python3
"""
扬说财经 · 口播音频生成器 v4.0
核心原则：纯文本直传，不做任何 SSML 封装。
  - edge-tts 的 SSML/mstts 扩展解析不稳定，XML标签会被朗读为"网址乱码"
  - 脚本内容本身已是自然口播风格，无需额外标记
  - 仅通过 voice / rate / pitch 参数做基础调节

流程：先出脚本 → 专人审核 → 再生成音频

用法:
  python scripts/upgrade-audio.py                    # 今日早报+晚报
  python scripts/upgrade-audio.py --edition morning   # 仅早报
  python scripts/upgrade-audio.py --script-only       # 仅出脚本，不生成音频
  python scripts/upgrade-audio.py --from-script morning  # 从已审核脚本生成音频
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ================================================================
# 口播稿生成 — 像朋友聊天，不是播新闻
# ================================================================

def generate_script(session, title, storyboard, article_text, article_html=None):
    if session == 'morning':
        return _gen_morning(storyboard, article_text)
    else:
        return _gen_evening(storyboard, article_text)


def _gen_morning(panels, article_text):
    L = []

    # === 开场 ===
    L.append('朋友们早上好，我是阿扬。')
    L.append('')

    # === 全天新闻速览 ===
    L.append('先快速过一下今天重要的财经新闻。')
    L.append('')
    L.append('隔夜美股全线反弹，纳斯达克涨了1.59%，费城半导体指数大涨4.49%。')
    L.append('国际油价这边不太平——WTI原油暴跌5.66%，直接跌破了100美元关口。')
    L.append('A股昨天半导体先涨为敬，华虹半导体大涨18%，中芯国际涨了8%。')
    L.append('')
    L.append('不过这些都不是今天的主角。')
    L.append('')

    # === 深度板块：英伟达财报 ===
    kw = '816'
    need_nvidia = kw in article_text or any(kw in p.get('dialogue','') for p in panels)
    if not need_nvidia:
        need_nvidia = any('英伟达' in p.get('dialogue','') for p in panels)
    if not need_nvidia:
        need_nvidia = any('英伟达' in p.get('titleText','') for p in panels)

    if need_nvidia:
        L.append('今天的主角是英伟达——它昨晚交了一份让华尔街集体沉默了三分钟的财报。')
        L.append('一天赚6.4亿美元是什么概念呢？你睡八个小时，它进账两亿多美元。')
        L.append('有些上市公司一年都赚不了这么多。')
        L.append('')

        L.append('咱们先看硬数字。')
        L.append('营收816亿美元，同比增长85%。净利润583亿美元，同比增长211%。')
        L.append('注意看这个211%——说明英伟达不光在卖更多芯片，利润率也在飙升。')
        L.append('这不是以量换价，这是量价齐升。')
        L.append('')

        L.append('更吓人的是二季度指引——910亿美元。')
        L.append('市场预期的868亿？直接踩碎。')
        L.append('黄仁勋说这话的时候，华尔街的交易员们一边抹冷汗一边按计算器。')
        L.append('')

        L.append('你可能会问：一家卖显卡的公司，凭什么这么赚钱？')
        L.append('其实英伟达早就不光是卖显卡了。')
        L.append('数据中心业务752亿美元，占总营收的92%。')
        L.append('全世界的科技巨头都在抢它的芯片。')
        L.append('这就好比淘金热的时候，大家都在挖金子，但真正赚钱的是那个卖铲子的人。')
        L.append('英伟达就是那把铲子的唯一供应商。')
        L.append('')

        L.append('对A股来说，半导体板块昨天已经提前反应。')
        L.append('华虹半导体大涨18%，中芯国际涨8%。')
        L.append('但说句不好听的——A股映射英伟达，就像在淘宝看卖家秀。')
        L.append('英伟达赚一块钱，映射股不一定能赚一分。')
        L.append('短期追高的事，自己心里要有数。')
        L.append('')

    # === 油价板块补充 ===
    L.append('再提一句油价。')
    L.append('WTI原油跌了5.66%，这个跌幅不小。')
    L.append('原因也不复杂——全球经济复苏的预期在降温，加上主要产油国在增产。')
    L.append('油价下移对运输和化工是利好，但对资源出口国就不太妙了。')
    L.append('')

    # === 收尾 ===
    L.append('最后，分享一句话吧——')
    L.append('英伟达的财报不是成绩单，是人工智能时代的账单。全世界都在买单。')
    L.append('')
    L.append('好，今天的早报就到这儿。我是阿扬，我们明天见。')

    return '\n'.join(L)


def _detect_topic(article_text, panels):
    """检测文章主题，返回主题标识"""
    text = (article_text or '') + ' ' + ' '.join(p.get('dialogue', '') for p in panels)
    if any(kw in text for kw in ['天地板', '4700', '沪指跌', '暴跌', '诱多出货', '跳水']):
        return 'astock-crash'
    if any(kw in text for kw in ['黄金', '金价', '金饰', 'AU9999']):
        return 'gold'
    return 'general'


def _gen_evening(panels, article_text):
    topic = _detect_topic(article_text, panels)
    L = []

    # === 共同开头 ===
    L.append('晚上好朋友们，我是阿扬。')
    L.append('')

    if topic == 'astock-crash':
        # ===== A股天地板 版本 =====
        L.append('今天A股走出了一个教科书级的行情——早盘高开，午后跳水。')
        L.append('')
        L.append('沪指跌了2.04%，失守4100点。全市场超4700只个股下跌，仅约700只上涨。')
        L.append('成交额3.51万亿，主力资金净流出1724亿。可谓放量下跌，恐慌出逃。')
        L.append('')
        L.append('跌得最惨的是半导体板块。十余只个股跌超10%，前两天涨的全还回去了。')
        L.append('')
        L.append('但问题来了——为什么跌这么突然？')
        L.append('导火索在中东。')
        L.append('')
        L.append('特朗普表示美伊谈判进入最后阶段，协议可能在数小时内公布。')
        L.append('WTI原油应声暴跌5.66%，跌破100美元关口，收报98.26美元一桶。')
        L.append('')
        L.append('有意思的是，同样的消息到了美股和A股，解读完全不一样。')
        L.append('美股理解成通胀降温利好科技，费城半导体大涨4.5%，纳指涨了1.54%。')
        L.append('A股的理解是——中东要出事了，先跑为敬。')
        L.append('')
        L.append('半导体作为风险偏好最高的板块，首当其冲。主力资金一天净流出287亿。')
        L.append('其实这也不能全怪散户，A股这种情绪放大的结构，消息怎么传都会变味。')
        L.append('')
        L.append('但今天也不是全都跌。')
        L.append('')
        L.append('建设银行创了历史新高，银行板块全天净流入23.5亿。')
        L.append('机场航运受益油价暴跌大涨，春秋航空领涨。这些是用油大户，成本直接降了。')
        L.append('白酒底部信号出现，人形机器人也有资金在布局。')
        L.append('')
        L.append('说句实在话——每次放量暴跌，都是资金从高位板块切向低位板块的过程。')
        L.append('今天半导体里的钱出来，并没有离开市场，而是去了银行和航运。')
        L.append('3.51万亿的成交说明市场不缺钱，缺的是方向。')
        L.append('')
        L.append('那普通人接下来怎么办？三条建议。')
        L.append('')
        L.append('第一，别追高半导体。前面涨了15%你没赶上，现在接飞刀不划算。')
        L.append('当然，持仓被套的也别慌——AI产业链的基本面没变，英伟达财报超预期，调整只是涨快了需要消化。')
        L.append('')
        L.append('第二，关注油价暴跌的受益链。航空、化工、物流，成本下降会逐步体现在财报里。')
        L.append('')
        L.append('第三，保持耐心。缩量企稳才是底部信号，现在放量下跌的时候猜底，大概率猜不准。')
        L.append('')

    elif topic == 'gold':
        # ===== 黄金 版本 =====
        L.append('先看今天全球市场的收盘情况。')
        L.append('')
        L.append('美股这边，纳斯达克涨了1.59%，费城半导体大涨4.49%，英伟达财报把整个半导体板块都带起来了。')
        L.append('美元指数继续走弱，跌到了99.09，创了近期新低。')
        L.append('国际油价大幅下跌，WTI原油跌了5.66%。')
        L.append('')
        L.append('不过今天咱们重点聊一个让很多人又爱又恨的话题——黄金。')
        L.append('')
        L.append('先说数据。')
        L.append('COMEX黄金期货今天收报4546美元一盎司，涨了0.78%。')
        L.append('现货黄金更猛，涨了1.35%，到了4543美元。')
        L.append('')
        L.append('国内这边，上海黄金交易所的AU9999收盘报999块7一克，离1000块就差三毛钱。')
        L.append('沪金期货更干脆，直接突破了1000元大关，最高触及1002块7毛8。')
        L.append('')
        L.append('半年前你觉得500多一克的金价贵了，现在回头看——那是真便宜。')
        L.append('菜百首饰的零售价已经到1372一克了，金条也得1180。')
        L.append('黄金ETF的持仓也创了新高，全球净流入66亿美元。')
        L.append('')
        L.append('但真正值得关注的，不是金店门口排队的大妈——而是那些不差钱的顶级玩家。')
        L.append('')
        L.append('你知道吗，这一轮金价上涨，跟以前完全不一样。')
        L.append('以前是散户追涨、大妈抢金，这次是各国央行在买。')
        L.append('')

        need_cbank = '央行' in article_text or any('央行' in p.get('dialogue','') for p in panels)
        if need_cbank:
            L.append('全球央行一季度买了324吨黄金。中国连续18个月增持，根本停不下来。')
            L.append('4月末黄金储备达到2321.56吨，环比又增了8.09吨。')
            L.append('关键在这里——央行利用3到4月的金价回调窗口，在加速买。')
            L.append('金价跌了？那不叫跌，那叫打折促销。')
            L.append('')
            L.append('央行买金和散户买金完全是两码事。')
            L.append('散户买金是投机，央行买金是在给美元信用投反对票。')
            L.append('')
            L.append('2022年俄罗斯的外汇储备被冻结之后，全世界央行都醒了。')
            L.append('它们心里在想：如果美国哪天不高兴，把我存的美元也冻了怎么办？')
            L.append('黄金是世界上唯一没有对方违约风险的资产。')
            L.append('你持有黄金，不需要担心任何政府违约。')
            L.append('')

        L.append('所以这一轮金价上涨，不是单一因素，而是三重力量同时发力、互相放大。')
        L.append('')
        L.append('第一，去美元化。中国黄金储备占官方储备只有9.1%，全球均值在15%左右，还有很大的增持空间。')
        L.append('')
        L.append('第二，降息预期。美联储4月会议纪要放了鹰，但市场根本不买账。美元指数一路跌到99。实际利率下行，黄金的持有成本就降低了。')
        L.append('')
        L.append('第三，地缘风险。美伊谈判说进入最终阶段，但还没踏实。这个世界不缺故事，缺的是确定性的锚。黄金就是那个锚。')
        L.append('')
        L.append('有人会说：每次金价涨都有人说这次不一样，是不是又在忽悠人？')
        L.append('说实话，这次还真不一样。')
        L.append('')
        L.append('第一，央行从卖家变成了买家。过去几轮黄金牛市，央行是悄悄高位出货的。而这一轮，央行是持续买入的主买家。')
        L.append('')
        L.append('第二，金价和实际利率脱钩了。美联储加了11次息，金价不跌反涨。央行购金这个第三只手，打破了传统定价模型。')
        L.append('')
        L.append('第三，东西方同步买入。全球黄金ETF净流入66亿美元，欧洲净流入37亿领跑，亚洲连续8个月净流入。东也在买，西也在买。这是共识，不是博弈。')
        L.append('')

        need_advice = '普通人' in article_text
        if need_advice:
            L.append('好，说到这你可能会问：那普通人该怎么办？三点建议。')
            L.append('')
            L.append('第一，别买金饰当投资。1372一克的首饰金，里面有品牌溢价、有工费、有消费税。那是消费。金条1180一克，那才是真金的价格。')
            L.append('')
            L.append('第二，黄金占资产组合的5%到10%就够了。它不产生利息，不看PE，不看增长率。它是你资产里的安全带——平时觉得多余，真出事的时候才知道它的好。')
            L.append('')
            L.append('第三，别追高。金价从低点已经翻倍了，一把冲进去万一回调心态容易崩。定投慢慢买，比一把梭舒服得多。')
            L.append('')

        L.append('最后，分享一句我很认同的话。')
        L.append('黄金之所以叫黄金，不是因为它的颜色——')
        L.append('而是因为几千年来，人们在最慌的时候，最先想到的永远都是它。')
        L.append('')

    else:
        # ===== 通用版本：按面板对话逐段展开 =====
        L.append('先快速过一下今天的财经要点。')
        L.append('')
        for i, p in enumerate(panels):
            dialogue = p.get('dialogue', '').strip()
            title = p.get('titleText', '').strip()
            if not dialogue:
                continue
            if i == 0:
                L.append(dialogue)
                L.append('')
            elif i == len(panels) - 1:
                L.append('最后，' + dialogue)
                L.append('')
            else:
                L.append(dialogue)
                L.append('')

    # === 共同收尾 ===
    L.append('好的，今天就聊到这儿。朋友们晚安，我是阿扬，明天见。')

    return '\n'.join(L)


# ================================================================
# Edge TTS 生成 — 纯文本直传，SSML 已全部移除
# SSML 中 mstts:express-as / prosody / break 等标签会被朗读为
# 文本中的"乱码网址"，因此全部禁用。
# ================================================================

async def generate_edge_tts(text, output_path):
    import edge_tts
    # 纯文本直传，只指定音色和语速
    # rate 必须以 + 或 - 开头，-5% 为略慢（更自然的口播节奏）
    communicate = edge_tts.Communicate(
        text=text,
        # zh-CN-YunyangNeural 专业男声，分类为 News，Personality: Professional, Reliable
        # 比 XiaoxiaoNeural 更沉稳、更具播报感，听众更容易听进去
        voice='zh-CN-YunyangNeural',
        rate='-5%',
    )
    await communicate.save(output_path)
    size_kb = os.path.getsize(output_path) / 1024
    print('[Edge TTS] OK: %s (%.0f KB)' % (output_path, size_kb))
    return True


# ================================================================
# Main
# ================================================================

def generate_and_save_script(session):
    """生成口播脚本并保存到文件，返回(script_text, title)。不生成音频。"""
    today = time.strftime('%Y-%m-%d')
    edition_dir = os.path.join(ROOT, today, 'wechat-publish', session)

    storyboard_path = os.path.join(edition_dir, 'storyboard.json')
    article_path = os.path.join(edition_dir, 'article.md')
    html_path = os.path.join(edition_dir, 'article.html')

    if not os.path.exists(storyboard_path):
        print('[!] 未找到 storyboard:', storyboard_path)
        return None, None

    with open(storyboard_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title = data.get('articleTitle', '')
    panels = data.get('panels', [])

    article_text = ''
    if os.path.exists(article_path):
        with open(article_path, 'r', encoding='utf-8') as f:
            article_text = f.read()

    article_html = ''
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            article_html = f.read()

    label = 'MORNING' if session == 'morning' else 'EVENING'
    print('\n' + '=' * 50)
    print('  %s: %s' % (label, title))
    print('=' * 50)

    script = generate_script(session, title, panels, article_text, article_html)

    print('\n[脚本草稿]')
    for line in script.strip().split('\n')[:15]:
        print('  ' + (line if line.strip() else ''))
    print('  ...(%d chars)' % len(script))

    # 保存脚本文本（供专人审核）
    script_path = os.path.join(edition_dir, 'script.txt')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script)
    print('\n[✓] 口播脚本已保存: %s' % script_path)

    # 快速检查：提醒英文词汇
    eng_letters = re.findall(r'[a-zA-Z]{2,}', script)
    if eng_letters:
        print('[!] 注意: 脚本中含英文词汇: %s' % ', '.join(set(eng_letters)))

    return script, title


def process_edition(session, skip_audio=False):
    """完整流程：生成脚本 → 保存 → 生成音频"""
    script, title = generate_and_save_script(session)
    if script is None:
        return False

    if skip_audio:
        print('\n[--script-only 模式] 已跳过音频生成')
        print('  审核脚本后运行: python scripts/upgrade-audio.py --from-script %s' % session)
        return True

    today = time.strftime('%Y-%m-%d')
    edition_dir = os.path.join(ROOT, today, 'wechat-publish', session)
    output_path = os.path.join(edition_dir, 'audio.mp3')
    print('\n[Edge TTS] 正在生成音频...')
    asyncio.run(generate_edge_tts(script, output_path))
    label = 'MORNING' if session == 'morning' else 'EVENING'
    print('[OK] %s audio done' % label)

    # 提示审核流程
    print('\n' + '-' * 40)
    print('  审核流程提醒:')
    print('  1. 打开 script.txt 审核脚本文本')
    print('  2. 确认无英文字母/网址/异常符号')
    print('  3. 如有修改，直接编辑 script.txt')
    print('  4. 重新运行: python scripts/upgrade-audio.py --from-script %s' % session)
    print('-' * 40)
    return True


def process_from_script(session):
    """从已审核的 script.txt 直接生成音频（跳过脚本生成）"""
    today = time.strftime('%Y-%m-%d')
    edition_dir = os.path.join(ROOT, today, 'wechat-publish', session)
    script_path = os.path.join(edition_dir, 'script.txt')

    if not os.path.exists(script_path):
        print('[!] 未找到已审核脚本: %s' % script_path)
        print('   请先运行 python scripts/upgrade-audio.py --edition %s 生成脚本' % session)
        return False

    with open(script_path, 'r', encoding='utf-8') as f:
        script = f.read()

    print('\n[使用已审核脚本] %s (%d chars)' % (script_path, len(script)))

    # 快速检查：提醒英文字母
    eng_letters = re.findall(r'[a-zA-Z]{2,}', script)
    if eng_letters:
        print('[!] 警告: 脚本中含英文词汇: %s' % ', '.join(set(eng_letters)))
        print('   TTS可能逐字母朗读，建议替换为中文')

    output_path = os.path.join(edition_dir, 'audio.mp3')
    print('\n[Edge TTS] 正在生成音频...')
    asyncio.run(generate_edge_tts(script, output_path))
    print('[OK] %s audio done (from script)' % session)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='扬说财经 · 口播音频生成器 v4.0')
    parser.add_argument('--edition', choices=['morning', 'evening'],
                        help='生成指定版次的口播脚本+音频')
    parser.add_argument('--from-script', choices=['morning', 'evening'],
                        help='从已审核的 script.txt 直接生成音频')
    parser.add_argument('--script-only', choices=['morning', 'evening'],
                        help='仅生成口播脚本，不生成音频')
    args = parser.parse_args()

    print('=' * 50)
    print('   扬说财经 · 口播音频生成器 v4.0')
    print('   纯文本直传 — 无SSML — 无乱码')
    print('=' * 50)

    if args.from_script:
        process_from_script(args.from_script)
    elif args.script_only:
        process_edition(args.script_only, skip_audio=True)
    elif args.edition:
        process_edition(args.edition)
    else:
        process_edition('morning')
        process_edition('evening')

    print('\nDone!')
