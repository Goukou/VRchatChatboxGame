import random
import time
from pythonosc.udp_client import SimpleUDPClient

# --- VRChat OSC 配置 ---
osc_ip: str = "127.0.0.1"
osc_port: int = 9000

client = SimpleUDPClient(osc_ip, osc_port)

# --- 游戏参数 ---
# 因为点(.)比较窄，为了视觉效果好一点，把跑道视觉长度稍微设长一点 (比如 15)
TRACK_VISUAL_LENGTH = 15  
TOTAL_LAPS = 3            # 总共跑3圈
FINISH_LINE = TRACK_VISUAL_LENGTH * TOTAL_LAPS 

HORSES = [
    {"name": "1号", "icon": "🐎①"},
    {"name": "2号", "icon": "🐎②"},
    {"name": "3号", "icon": "🐎③"},
    {"name": "4号", "icon": "🐎④"},
]

def send_to_vrc(text):
    try:
        # direct_mode=True, sound=False
        client.send_message("/chatbox/input", [text, True, False])
        print(f"\n--- OSC发送 ---\n{text}") 
    except Exception as e:
        print(f"发送出错: {e}")

def start_race():
    positions = [0] * len(HORSES)
    winner = None
    
    # 倒计时
    for i in range(3, 0, -1):
        send_to_vrc(f"⏳ 赛马准备... {i}\n(总共 {TOTAL_LAPS} 圈)")
        time.sleep(1)

    send_to_vrc("比赛开始！")
    time.sleep(1)
    
    while not winner:
        # 顶部信息
        msg_lines = [f"🏆 目标: {TOTAL_LAPS}圈 🏆"]
        msg_lines.append("-" * 20)

        for i, horse in enumerate(HORSES):
            # 1. 移动 (3秒一次，步子设大一点 1-5格)
            step = random.randint(1, 5)
            if random.random() < 0.1: # 暴击
                step += 3
            
            positions[i] += step
            if positions[i] > FINISH_LINE:
                positions[i] = FINISH_LINE

            # 2. 计算视觉位置
            current_pos = positions[i]
            current_lap = int(current_pos / TRACK_VISUAL_LENGTH) + 1
            if current_lap > TOTAL_LAPS: current_lap = TOTAL_LAPS
            
            # 在当前圈的位置 (0 到 14)
            visual_pos = current_pos % TRACK_VISUAL_LENGTH
            
            # 如果跑完了，强制停在最右边
            if current_pos >= FINISH_LINE:
                visual_pos = TRACK_VISUAL_LENGTH - 1
                status_str = "🏁FIN"
            else:
                status_str = f"圈{current_lap}"

            # 3. 绘制全点跑道
            # 左边是点，右边也是点，中间是马
            left_track = "." * visual_pos 
            right_track = "." * (TRACK_VISUAL_LENGTH - visual_pos - 1)
            
            # 组合： |......🐎①........|
            line = f"|{left_track}{horse['icon']}{right_track}| {status_str}"
            msg_lines.append(line)

            if current_pos >= FINISH_LINE:
                if winner is None:
                    winner = horse['name']

        # 发送
        full_msg = "\n".join(msg_lines)
        send_to_vrc(full_msg)

        if not winner:
            time.sleep(3) # 严格遵守3秒刷新

    return winner
	
def main():
    print(f"正在连接 VRChat ({osc_ip}:{osc_port})...")
    
    while True:
        winner = start_race()
        
        end_msg = (
            f"🎉 比赛结束 🎉\n"
            f"================\n"
            f"   👑 冠军: {winner} \n"
            f"================\n"
            f"(10秒后重开)"
        )
        send_to_vrc(end_msg)
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        client.send_message("/chatbox/input", ["", True, False])
        print("已退出。")