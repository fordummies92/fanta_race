import openpyxl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as mpatches
import numpy as np

# ── 1. PARSING ────────────────────────────────────────────────────────────────

def parse_result(result_str):
    """Restituisce (punti_casa, punti_ospite) dati i punti classifica."""
    if not result_str or result_str == '-':
        return None
    try:
        g_casa, g_ospite = result_str.split('-')
        g_casa, g_ospite = int(g_casa), int(g_ospite)
        if g_casa > g_ospite:
            return (3, 0)
        elif g_casa == g_ospite:
            return (1, 1)
        else:
            return (0, 3)
    except Exception:
        return None

def parse_excel(path):
    """
    Restituisce una lista di giornate, ordinate per numero giornata.
    Ogni giornata è una lista di tuple: (casa, ospite, pts_casa, pts_ospite)
    """
    wb = openpyxl.load_workbook(path)
    ws = wb['Calendario']

    matchdays = {}  # giornata_num -> lista di partite

    rows = list(ws.iter_rows(min_row=4, values_only=True))

    i = 0
    while i < len(rows):
        row = rows[i]
        # Riga header: contiene "Xª Giornata lega"
        left_header = row[0]
        right_header = row[6]

        if isinstance(left_header, str) and 'Giornata lega' in left_header:
            # Estrai numero giornata
            left_num = int(left_header.split('ª')[0])
            right_num = int(right_header.split('ª')[0]) if isinstance(right_header, str) and 'Giornata lega' in right_header else None

            if left_num not in matchdays:
                matchdays[left_num] = []
            if right_num and right_num not in matchdays:
                matchdays[right_num] = []

            # Leggi le 5 partite successive
            for j in range(1, 6):
                if i + j >= len(rows):
                    break
                match_row = rows[i + j]

                # Blocco sinistro: col 0,1,2,3,4
                casa_l, pts_c_l, pts_o_l, ospite_l, res_l = match_row[0], match_row[1], match_row[2], match_row[3], match_row[4]
                pts = parse_result(res_l)
                if pts and casa_l and ospite_l:
                    matchdays[left_num].append((str(casa_l), str(ospite_l), pts[0], pts[1]))

                # Blocco destro: col 6,7,8,9,10
                if right_num:
                    casa_r, pts_c_r, pts_o_r, ospite_r, res_r = match_row[6], match_row[7], match_row[8], match_row[9], match_row[10]
                    pts2 = parse_result(res_r)
                    if pts2 and casa_r and ospite_r:
                        matchdays[right_num].append((str(casa_r), str(ospite_r), pts2[0], pts2[1]))

            i += 6  # salta header + 5 partite
        else:
            i += 1

    return matchdays


# ── 2. CALCOLO CLASSIFICA CUMULATIVA ─────────────────────────────────────────

def compute_standings(matchdays):
    """
    Restituisce:
    - teams: lista squadre
    - standings_over_time: list of dicts {team: punti_cumulativi} per ogni giornata
    - giornate_labels: lista etichette
    """
    # Trova tutte le squadre
    teams = set()
    for matches in matchdays.values():
        for casa, ospite, _, _ in matches:
            teams.add(casa)
            teams.add(ospite)
    teams = sorted(teams)

    # Cumula punti giornata per giornata
    current_pts = {t: 0 for t in teams}
    standings_over_time = []
    giornate_labels = []

    for giornata_num in sorted(matchdays.keys()):
        matches = matchdays[giornata_num]
        if not matches:
            continue
        for casa, ospite, pts_c, pts_o in matches:
            current_pts[casa] += pts_c
            current_pts[ospite] += pts_o
        standings_over_time.append(dict(current_pts))
        giornate_labels.append(f'G{giornata_num}')

    return teams, standings_over_time, giornate_labels


# ── 3. ANIMAZIONE BAR CHART RACE ─────────────────────────────────────────────

COLORS = [
    '#e63946', '#457b9d', '#2a9d8f', '#e9c46a', '#f4a261',
    '#264653', '#a8dadc', '#6d6875', '#b5838d', '#ffb4a2'
]

STEPS = 30        # frame interpolati tra una giornata e la successiva
HOLD_FRAMES = 8   # frame fermi sulla giornata prima di passare alla prossima
FPS = 30

def ease_in_out(t):
    """Curva smooth: accelera all'inizio, decelera alla fine."""
    return t * t * (3 - 2 * t)

def rank_positions(data):
    """Restituisce {team: y_position} con posizione 0 = primo in classifica (top)."""
    sorted_teams = sorted(data.keys(), key=lambda t: (-data[t], t))
    n = len(sorted_teams)
    return {team: (n - 1 - i) for i, team in enumerate(sorted_teams)}

def build_frames(standings_over_time, giornate_labels):
    """
    Costruisce tutti i frame interpolati.
    Ogni frame è (pts_interp, y_interp, label) dove:
      pts_interp = {team: valore_barra}
      y_interp   = {team: posizione_y}
      label      = stringa giornata
    """
    frames = []
    n = len(standings_over_time)

    for i in range(n):
        data_cur = standings_over_time[i]
        data_next = standings_over_time[i + 1] if i + 1 < n else data_cur
        label_cur = giornate_labels[i]
        label_next = giornate_labels[i + 1] if i + 1 < n else label_cur

        ranks_cur = rank_positions(data_cur)
        ranks_next = rank_positions(data_next)

        # Frame fermi sulla giornata corrente
        for _ in range(HOLD_FRAMES):
            frames.append((dict(data_cur), dict(ranks_cur), label_cur))

        # Frame di transizione verso la prossima
        if i + 1 < n:
            for step in range(STEPS):
                t = ease_in_out((step + 1) / STEPS)
                pts_interp = {
                    team: data_cur[team] + t * (data_next[team] - data_cur[team])
                    for team in data_cur
                }
                y_interp = {
                    team: ranks_cur[team] + t * (ranks_next[team] - ranks_cur[team])
                    for team in data_cur
                }
                # Etichetta: mostra la prossima solo a metà transizione
                label = label_next if t >= 0.5 else label_cur
                frames.append((pts_interp, y_interp, label))

    return frames

def make_animation(teams, standings_over_time, giornate_labels):
    n_teams = len(teams)
    color_map = {team: COLORS[i % len(COLORS)] for i, team in enumerate(sorted(teams))}
    max_pts = max(max(d.values()) for d in standings_over_time)

    all_frames = build_frames(standings_over_time, giornate_labels)

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#1a1a2e')

    def draw_frame(frame_idx):
        ax.clear()
        ax.set_facecolor('#16213e')

        pts_interp, y_interp, label = all_frames[frame_idx]

        for team in teams:
            y = y_interp[team]
            pts = pts_interp[team]
            color = color_map[team]

            ax.barh(y, pts, color=color, height=0.7,
                    edgecolor='white', linewidth=0.3, align='center')
            ax.text(-0.5, y, team, va='center', ha='right',
                    color='white', fontsize=11, fontweight='bold')
            ax.text(pts + 0.4, y, f'{pts:.0f}', va='center', ha='left',
                    color='white', fontsize=10, fontweight='bold')

        ax.set_xlim(-13, max_pts + 6)
        ax.set_ylim(-0.8, n_teams - 0.2)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.tick_params(axis='x', colors='white')

        ax.set_title('Classifica Fantacalcio — Guasconemessicano',
                     color='white', fontsize=14, fontweight='bold', pad=15)
        ax.text(0.98, 0.02, label,
                transform=ax.transAxes, color='#aaaaaa',
                fontsize=28, fontweight='bold', ha='right', va='bottom', alpha=0.6)

        fig.tight_layout(rect=[0.15, 0, 1, 1])

    ani = animation.FuncAnimation(fig, draw_frame, frames=len(all_frames),
                                  interval=1000 // FPS, repeat=True)
    return fig, ani


# ── 4. LINE CHART ANIMATO ────────────────────────────────────────────────────

LINE_STEPS = 20   # frame interpolati tra una giornata e la successiva (line)
LINE_HOLD  = 6    # frame fermi sulla giornata

def make_line_animation(teams, standings_over_time, giornate_labels):
    """
    Line chart: asse X = giornate, asse Y = punti cumulativi.
    Le linee crescono giornata per giornata con interpolazione smooth.
    """
    color_map = {team: COLORS[i % len(COLORS)] for i, team in enumerate(sorted(teams))}
    n_gior = len(giornate_labels)
    max_pts = max(max(d.values()) for d in standings_over_time)

    # Prepara i dati: pts_matrix[team][giornata_idx] = punti
    pts_matrix = {team: [0] + [standings_over_time[g][team] for g in range(n_gior)]
                  for team in teams}
    x_labels = ['Start'] + giornate_labels  # indice 0 = 0 punti

    # Costruisce i frame: (x_end, frac) dove disegniamo da 0 a x_end + frac
    frames_meta = []
    for i in range(n_gior):
        # hold sulla giornata i (indice i+1 nei dati)
        for _ in range(LINE_HOLD):
            frames_meta.append((i + 1, 1.0))
        # transizione verso giornata i+1
        if i + 1 < n_gior:
            for step in range(LINE_STEPS):
                t = ease_in_out((step + 1) / LINE_STEPS)
                frames_meta.append((i + 1, t))

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor('#1a1a2e')

    def draw_line_frame(frame_idx):
        ax.clear()
        ax.set_facecolor('#16213e')

        seg_end, frac = frames_meta[frame_idx]
        # indici x interi già disegnati: 0..seg_end
        # + punto interpolato a seg_end + frac (se frac < 1)

        for team in teams:
            color = color_map[team]
            full_pts = pts_matrix[team]

            # Punti già "rivelati"
            xs = list(range(seg_end + 1))
            ys = full_pts[:seg_end + 1]

            # Punto interpolato verso la prossima giornata
            if frac < 1.0 and seg_end + 1 < len(full_pts):
                x_next = seg_end + frac
                y_next = full_pts[seg_end] + frac * (full_pts[seg_end + 1] - full_pts[seg_end])
                xs = xs + [x_next]
                ys = ys + [y_next]

            ax.plot(xs, ys, color=color, linewidth=2.5, solid_capstyle='round')
            ax.plot(xs[-1], ys[-1], 'o', color=color, markersize=6)

            # Etichetta finale
            ax.text(xs[-1] + 0.05, ys[-1], team, color=color,
                    fontsize=8.5, fontweight='bold', va='center')

        # Giornata corrente evidenziata
        cur_gior_idx = seg_end if frac < 0.5 or seg_end + 1 >= n_gior else seg_end + 1
        cur_label = x_labels[cur_gior_idx] if cur_gior_idx < len(x_labels) else x_labels[-1]

        ax.set_xlim(-0.3, n_gior + 2.5)
        ax.set_ylim(-2, max_pts + 5)

        # Tick X: mostra solo giornate già rivelate ogni 2
        shown = list(range(0, seg_end + 1, 2)) + ([seg_end] if seg_end % 2 != 0 else [])
        ax.set_xticks(shown)
        ax.set_xticklabels([x_labels[i] for i in shown], color='#aaaaaa', fontsize=8, rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.yaxis.label.set_color('white')

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('#444')
        ax.spines['left'].set_color('#444')
        ax.grid(axis='y', color='#333', linewidth=0.5, linestyle='--')

        ax.set_title('Punti nel tempo — Guasconemessicano',
                     color='white', fontsize=14, fontweight='bold', pad=15)
        ax.text(0.98, 0.02, cur_label,
                transform=ax.transAxes, color='#aaaaaa',
                fontsize=26, fontweight='bold', ha='right', va='bottom', alpha=0.5)

        fig.tight_layout()

    ani = animation.FuncAnimation(fig, draw_line_frame, frames=len(frames_meta),
                                  interval=1000 // FPS, repeat=True)
    return fig, ani


# ── 5. MAIN ───────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    import os
    path = os.path.join(os.path.dirname(__file__), 'Calendario_Guasconemessicano.xlsx')

    print("Parsing Excel...")
    matchdays = parse_excel(path)
    print(f"Giornate trovate: {sorted(matchdays.keys())}")

    print("Calcolo classifica cumulativa...")
    teams, standings_over_time, giornate_labels = compute_standings(matchdays)
    print(f"Squadre: {teams}")
    print(f"Giornate elaborate: {giornate_labels}")

    # Stampa classifica finale
    print("\n--- CLASSIFICA FINALE ---")
    final = standings_over_time[-1]
    for rank, (team, pts) in enumerate(sorted(final.items(), key=lambda x: -x[1]), 1):
        print(f"{rank:2}. {team:<25} {pts} punti")

    print("\nGenerazione animazione...")
    fig, ani = make_animation(teams, standings_over_time, giornate_labels)

    out_gif = os.path.join(os.path.dirname(__file__), 'fanta_race.gif')
    out_mp4 = os.path.join(os.path.dirname(__file__), 'fanta_race.mp4')

    print(f"Salvo GIF → {out_gif}")
    ani.save(out_gif, writer='pillow', fps=FPS, dpi=100)
    print("GIF salvata!")

    try:
        print(f"Salvo MP4 → {out_mp4}")
        writer = animation.FFMpegWriter(fps=FPS, codec='libx264',
                                        extra_args=['-pix_fmt', 'yuv420p'])
        ani.save(out_mp4, writer=writer, dpi=120)
        print("MP4 salvato!")
    except Exception as e:
        print(f"MP4 non disponibile (ffmpeg non installato): {e}")

    plt.close(fig)
    print("\nFatto! Apri fanta_race.gif per vedere l'animazione.")

    # ── Line chart ──
    print("\nGenerazione line chart animato...")
    fig2, ani2 = make_line_animation(teams, standings_over_time, giornate_labels)

    out_gif2 = os.path.join(os.path.dirname(__file__), 'fanta_line.gif')
    out_mp4_2 = os.path.join(os.path.dirname(__file__), 'fanta_line.mp4')

    print(f"Salvo GIF → {out_gif2}")
    ani2.save(out_gif2, writer='pillow', fps=FPS, dpi=100)
    print("GIF line salvata!")

    try:
        print(f"Salvo MP4 → {out_mp4_2}")
        writer2 = animation.FFMpegWriter(fps=FPS, codec='libx264',
                                         extra_args=['-pix_fmt', 'yuv420p'])
        ani2.save(out_mp4_2, writer=writer2, dpi=120)
        print("MP4 line salvato!")
    except Exception as e:
        print(f"MP4 line non disponibile: {e}")

    plt.close(fig2)
    print("\nTutto fatto!")