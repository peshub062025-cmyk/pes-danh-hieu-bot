import discord
from discord.ext import commands
import sqlite3
import shlex
from flask import Flask
from threading import Thread

TOKEN = "DISCORD_TOKEN"

ADMIN_ID = 1222370876952154115
ALLOWED_CHANNEL = 1517725978208764106

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS solo (
    season INTEGER PRIMARY KEY,
    gold TEXT,
    silver TEXT,
    bronze TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS clan (
    season INTEGER,
    team_name TEXT,
    player TEXT
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS doi2x2 (
    season INTEGER,
    player TEXT
)
""")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"Đã đăng nhập: {bot.user}")

def dung_kenh(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL

def la_admin(ctx):
    return ctx.author.id == ADMIN_ID

@bot.command()
async def ping(ctx):

    if not dung_kenh(ctx):
        return

    await ctx.send("Bot đang hoạt động!")
@bot.command()
async def solo(ctx, season: int, *, players):

    if not dung_kenh(ctx):
        return

    if not la_admin(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    try:
        ds = shlex.split(players)

        if len(ds) != 3:
            await ctx.send(
                'Cú pháp: !solo 1 "Huu Tim" "Nam Beo" "Long CR7"'
            )
            return

        gold = ds[0]
        silver = ds[1]
        bronze = ds[2]

        cursor.execute(
            """
            INSERT INTO solo
            (season, gold, silver, bronze)
            VALUES (?, ?, ?, ?)
            """,
            (season, gold, silver, bronze)
        )

        conn.commit()

        await ctx.send(
            f"""🏆 SOLO MÙA {season}

🥇 {gold}
🥈 {silver}
🥉 {bronze}

Đã lưu thành công."""
        )

    except sqlite3.IntegrityError:
        await ctx.send("Mùa này đã tồn tại.")

@bot.command()
async def suasolo(ctx, season: int, *, players):

    if not dung_kenh(ctx):
        return

    if not la_admin(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    ds = shlex.split(players)

    if len(ds) != 3:
        await ctx.send(
            'Cú pháp: !suasolo 1 "Huu Tim" "Nam Beo" "Long CR7"'
        )
        return

    gold = ds[0]
    silver = ds[1]
    bronze = ds[2]

    cursor.execute(
        """
        UPDATE solo
        SET gold = ?, silver = ?, bronze = ?
        WHERE season = ?
        """,
        (gold, silver, bronze, season)
    )

    conn.commit()

    if cursor.rowcount == 0:
        await ctx.send(f"Không tìm thấy mùa {season}.")
    else:
        await ctx.send(
            f"""✏️ ĐÃ SỬA SOLO MÙA {season}

🥇 {gold}
🥈 {silver}
🥉 {bronze}
"""
        )

@bot.command()
async def clan(ctx, season: int, *, data):

    if not dung_kenh(ctx):
        return

    if not la_admin(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    ds = shlex.split(data)

    if len(ds) < 4:
        await ctx.send(
            'Cú pháp: !clan 1 "Tên Clan" "Người 1" "Người 2" "Người 3"'
        )
        return

    team_name = ds[0]
    players = ds[1:]

    cursor.execute(
        "SELECT * FROM clan WHERE season = ?",
        (season,)
    )

    if cursor.fetchone():
        await ctx.send("Mùa này đã tồn tại.")
        return

    for player in players:
        cursor.execute(
            """
            INSERT INTO clan
            (season, team_name, player)
            VALUES (?, ?, ?)
            """,
            (season, team_name, player)
        )

    conn.commit()

    msg = f"🏆 CLAN MÙA {season}\n\n"
    msg += f"Đội vô địch: {team_name}\n\n"

    for p in players:
        msg += f"🥇 {p}\n"

    msg += "\nĐã lưu thành công."

    await ctx.send(msg)
@bot.command()
async def suaclan(ctx, season: int, *, data):

    if not dung_kenh(ctx):
        return

    if not la_admin(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    ds = shlex.split(data)

    if len(ds) < 4:
        await ctx.send(
            'Cú pháp: !suaclan 1 "Tên Clan" "Người 1" "Người 2" "Người 3"'
        )
        return

    team_name = ds[0]
    players = ds[1:]

    cursor.execute(
        "SELECT * FROM clan WHERE season = ?",
        (season,)
    )

    if not cursor.fetchone():
        await ctx.send(f"Không tìm thấy mùa {season}.")
        return

    cursor.execute(
        "DELETE FROM clan WHERE season = ?",
        (season,)
    )

    for player in players:
        cursor.execute(
            """
            INSERT INTO clan
            (season, team_name, player)
            VALUES (?, ?, ?)
            """,
            (season, team_name, player)
        )

    conn.commit()

    msg = f"✏️ ĐÃ SỬA CLAN MÙA {season}\n\n"
    msg += f"Đội vô địch: {team_name}\n\n"

    for p in players:
        msg += f"🥇 {p}\n"

    await ctx.send(msg)

@bot.command(name="2x2")
async def doi2x2(ctx, season: int, *, data):

    if not dung_kenh(ctx):
        return

    if not la_admin(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    players = shlex.split(data)

    if len(players) != 4:
        await ctx.send(
            'Cú pháp: !2x2 1 "Huu Tim" "Nam Beo" "Long CR7" "Dat Messi"'
        )
        return

    cursor.execute(
        "SELECT * FROM doi2x2 WHERE season = ?",
        (season,)
    )

    if cursor.fetchone():
        await ctx.send("Mùa này đã tồn tại.")
        return

    for player in players:
        cursor.execute(
            """
            INSERT INTO doi2x2
            (season, player)
            VALUES (?, ?)
            """,
            (season, player)
        )

    conn.commit()

    msg = f"🏆 2x2 MÙA {season}\n\n"

    for p in players:
        msg += f"🥇 {p}\n"

    msg += "\nĐã lưu thành công."

    await ctx.send(msg)

@bot.command(name="sua2x2")
async def sua2x2(ctx, season: int, *, data):

    if not dung_kenh(ctx):
        return

    if not la_admin(ctx):
        await ctx.send("Bạn không có quyền sử dụng lệnh này.")
        return

    players = shlex.split(data)

    if len(players) != 4:
        await ctx.send(
            'Cú pháp: !sua2x2 1 "Huu Tim" "Nam Beo" "Long CR7" "Dat Messi"'
        )
        return

    cursor.execute(
        "SELECT * FROM doi2x2 WHERE season = ?",
        (season,)
    )

    if not cursor.fetchone():
        await ctx.send(f"Không tìm thấy mùa {season}.")
        return

    cursor.execute(
        "DELETE FROM doi2x2 WHERE season = ?",
        (season,)
    )

    for player in players:
        cursor.execute(
            """
            INSERT INTO doi2x2
            (season, player)
            VALUES (?, ?)
            """,
            (season, player)
        )

    conn.commit()

    msg = f"✏️ ĐÃ SỬA 2x2 MÙA {season}\n\n"

    for p in players:
        msg += f"🥇 {p}\n"

    await ctx.send(msg)

@bot.command()
async def tt(ctx, *, player):

    if not dung_kenh(ctx):
        return

    # ===== SOLO =====
    cursor.execute("""
        SELECT
            SUM(CASE WHEN gold = ? THEN 1 ELSE 0 END),
            SUM(CASE WHEN silver = ? THEN 1 ELSE 0 END),
            SUM(CASE WHEN bronze = ? THEN 1 ELSE 0 END)
        FROM solo
    """, (player, player, player))

    solo = cursor.fetchone()
    solo_gold = solo[0] or 0
    solo_silver = solo[1] or 0
    solo_bronze = solo[2] or 0

    # ===== CLAN (chỉ tính HCV cho team winner) =====
    cursor.execute("""
        SELECT COUNT(*)
        FROM clan
        WHERE player = ?
    """, (player,))

    clan_gold = cursor.fetchone()[0] or 0

    # ===== 2x2 (tất cả người trong danh sách đều nhận HCV) =====
    cursor.execute("""
        SELECT COUNT(*)
        FROM doi2x2
        WHERE player = ?
    """, (player,))

    doi2x2_gold = cursor.fetchone()[0] or 0

    # ===== OUTPUT =====
    total_gold = solo_gold + clan_gold + doi2x2_gold
    total_silver = solo_silver
    total_bronze = solo_bronze

    await ctx.send(f"""
🏆 THÀNH TÍCH {player}

📊 SOLO
🥇 {solo_gold}
🥈 {solo_silver}
🥉 {solo_bronze}

🏆 CLAN
🥇 {clan_gold}

🤝 2x2
🥇 {doi2x2_gold}

━━━━━━━━━━━━
🔥 TỔNG
🥇 {total_gold}
🥈 {total_silver}
🥉 {total_bronze}
""")

@bot.command()
async def bangvang(ctx):

    if not dung_kenh(ctx):
        return

    players = set()

    # ===== lấy tất cả player từ SOLO =====
    cursor.execute("SELECT gold, silver, bronze FROM solo")
    for g, s, b in cursor.fetchall():
        players.update([g, s, b])

    # ===== CLAN =====
    cursor.execute("SELECT player FROM clan")
    for (p,) in cursor.fetchall():
        players.add(p)

    # ===== 2x2 =====
    cursor.execute("SELECT player FROM doi2x2")
    for (p,) in cursor.fetchall():
        players.add(p)

    stats = {}

    # init
    for p in players:
        stats[p] = {"gold": 0, "silver": 0, "bronze": 0}

    # ===== SOLO =====
    cursor.execute("SELECT gold, silver, bronze FROM solo")
    for g, s, b in cursor.fetchall():

        if g in stats:
            stats[g]["gold"] += 1
        if s in stats:
            stats[s]["silver"] += 1
        if b in stats:
            stats[b]["bronze"] += 1

    # ===== CLAN (mỗi dòng = 1 HCV) =====
    cursor.execute("SELECT player FROM clan")
    for (p,) in cursor.fetchall():
        if p in stats:
            stats[p]["gold"] += 1

    # ===== 2x2 (mỗi người = 1 HCV) =====
    cursor.execute("SELECT player FROM doi2x2")
    for (p,) in cursor.fetchall():
        if p in stats:
            stats[p]["gold"] += 1

    # ===== SORT =====
    ranking = sorted(
        stats.items(),
        key=lambda x: (
            x[1]["gold"],
            x[1]["silver"],
            x[1]["bronze"]
        ),
        reverse=True
    )

    # ===== OUTPUT =====
    msg = "🏆 BẢNG VÀNG TOÀN GIẢI\n\n"

    rank = 1
    for p, s in ranking[:14]:

        msg += (
            f"{rank}. {p}\n"
            f"🥇 {s['gold']}  🥈 {s['silver']}  🥉 {s['bronze']}\n\n"
        )

        rank += 1

    await ctx.send(msg)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=run_web).start()

bot.run(TOKEN)
