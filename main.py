import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ─────────────────────────────────────────
#  ВВОД ДАННЫХ
# ─────────────────────────────────────────

print("=" * 50)
print(" АЛГОРИТМ ДЛЯ ПОИСКА КРАТЧАЙШЕГО ПУТИ")
print("=" * 50)

rows = int(input("\nСколько строк? "))
cols = int(input("Сколько столбцов? "))

print(f"\nГраф {rows}x{cols}. Всего узлов: {rows*cols}")

# ─────────────────────────────────────────
#  ВЫБОР МЕТОДА
# ─────────────────────────────────────────

print("\n" + "=" * 50)
print("Выбери метод:")
print("  1 — Форд-Беллман")
print("  2 — Минти (Дейкстра)")
method = input(" Вы выбрали: ").strip()

# ─────────────────────────────────────────
#  ВВОД ЧИСЕЛ ОДНИМ БЛОКОМ
# ─────────────────────────────────────────

print(f"""
вставьте все числа одним блоком, потом нажми Enter два раза:

  чередуй строки:
    горизонталь строки 1   ({cols-1} чисел)
    вертикаль  строки 1-2  ({cols} чисел)
    горизонталь строки 2   ({cols-1} чисел)
    ...
    горизонталь строки {rows}   ({cols-1} чисел)
""")

lines = []
while True:
    line = input()
    if line.strip() == "":
        break
    lines.append(line)

numbers = list(map(int, " ".join(lines).split()))

hE = []  # горизонтальные рёбра: hE[r][c] = ребро между (r,c) и (r,c+1)
vE = []  # вертикальные рёбра:   vE[r][c] = ребро между (r,c) и (r+1,c)
i = 0
for r in range(rows):
    hE.append(numbers[i:i+cols-1])
    i += cols-1
    if r < rows - 1:
        vE.append(numbers[i:i+cols])
        i += cols

INF = 10**9

# ─────────────────────────────────────────
#  МЕТОД 1: ФОРД-БЕЛЛМАН
#  начинаем из верхнего правого (0),
#  заполняем правую вертикаль и верхнюю горизонталь,
#  затем внутренние узлы — справа налево, сверху вниз.
#  Для каждого узла: min(d[r][c+1] + hE[r][c], d[r-1][c] + vE[r-1][c])
# ─────────────────────────────────────────

def ford_bellman():
    d = [[INF]*cols for _ in range(rows)]
    d[0][cols-1] = 0
    steps = []
    steps.append(f"Шаг 0: вписываем 0 в узел (0,{cols-1}) — верхний правый угол")

    # Правая вертикаль (сверху вниз)
    steps.append("\n--- Правая вертикаль (сверху вниз) ---")
    for r in range(1, rows):
        d[r][cols-1] = d[r-1][cols-1] + vE[r-1][cols-1]
        steps.append(f"  ({r},{cols-1}) = {d[r-1][cols-1]} + {vE[r-1][cols-1]} = {d[r][cols-1]}")

    # Верхняя горизонталь (справа налево)
    steps.append("\n--- Верхняя горизонталь (справа налево) ---")
    for c in range(cols-2, -1, -1):
        d[0][c] = d[0][c+1] + hE[0][c]
        steps.append(f"  (0,{c}) = {d[0][c+1]} + {hE[0][c]} = {d[0][c]}")

    # Внутренние узлы: сверху вниз, справа налево
    steps.append("\n--- Внутренние узлы (сверху вниз, справа налево) ---")
    for r in range(1, rows):
        for c in range(cols-2, -1, -1):
            via_right = d[r][c+1] + hE[r][c]        # из правого соседа
            via_up    = d[r-1][c] + vE[r-1][c]      # из верхнего соседа
            d[r][c] = min(via_right, via_up)
            steps.append(
                f"  ({r},{c}) = min(вправо: {d[r][c+1]}+{hE[r][c]}={via_right} ; "
                f"вверх: {d[r-1][c]}+{vE[r-1][c]}={via_up}) = {d[r][c]}"
            )

    return d, steps


# ─────────────────────────────────────────
#  МЕТОД 2: МИНТИ (Дейкстра)
#  1. Начинаем из верхнего правого, ставим 0, помечаем его.
#  2. Среди всех непомеченных вершин, смежных с хоть одной помеченной,
#     находим минимум (помеченная вершина + ребро).
#  3. Помечаем вершину(ы) с этим минимумом.
#  4. Повторяем до пока все вершины не помечены.
# ─────────────────────────────────────────

def minty():
    d    = [[INF]*cols for _ in range(rows)]
    done = [[False]*cols for _ in range(rows)]
    d[0][cols-1] = 0
    done[0][cols-1] = True
    steps = []
    steps.append(f"Шаг 0: вписываем 0 в узел (0,{cols-1}) — верхний правый угол")

    def neighbors(r, c):
        """Возвращает соседей узла (r,c) с весами рёбер"""
        res = []
        if c + 1 < cols:  res.append((r, c+1, hE[r][c]))      # правый
        if c - 1 >= 0:    res.append((r, c-1, hE[r][c-1]))    # левый
        if r + 1 < rows:  res.append((r+1, c, vE[r][c]))      # нижний
        if r - 1 >= 0:    res.append((r-1, c, vE[r-1][c]))    # верхний
        return res

    for step in range(1, rows * cols):
        # Собираем всех кандидатов: непомеченные вершины, достижимые из помеченных
        # Для каждого кандидата берём минимальное расстояние через помеченного соседа
        candidate_val = {}   # (r,c) -> минимальное расстояние
        candidate_from = {}  # (r,c) -> лучший помеченный сосед

        for r in range(rows):
            for c in range(cols):
                if done[r][c]:
                    # Смотрим всех непомеченных соседей этой помеченной вершины
                    for nr, nc, w in neighbors(r, c):
                        if not done[nr][nc]:
                            new_dist = d[r][c] + w
                            if (nr, nc) not in candidate_val or new_dist < candidate_val[(nr, nc)]:
                                candidate_val[(nr, nc)] = new_dist
                                candidate_from[(nr, nc)] = (r, c, w)

        if not candidate_val:
            break

        # Минимальное значение среди всех кандидатов
        best_val = min(candidate_val.values())

        # Формируем строку с кандидатами для вывода
        cand_strs = []
        for (nr, nc), val in sorted(candidate_val.items()):
            r_from, c_from, w = candidate_from[(nr, nc)]
            cand_strs.append(f"d[{r_from},{c_from}]+{w}={val}")

        steps.append(f"\nШаг {step}: рассматриваем: {' ; '.join(cand_strs)}")
        steps.append(f"          min = {best_val}")

        # Помечаем все вершины с минимальным значением
        for (nr, nc), val in candidate_val.items():
            if val == best_val and not done[nr][nc]:
                d[nr][nc] = best_val
                done[nr][nc] = True
                steps.append(f"          → вписываем {best_val} в ({nr},{nc})")

    return d, steps


# ─────────────────────────────────────────
#  ВОССТАНОВЛЕНИЕ ПУТИ
#  из нижнего левого угла идём назад.
#  Для текущей вершины со значением v проверяем всех соседей:
#  если v - вес_ребра == d[сосед], значит ребро входит в путь.
#  Защита от возврата: не идём в уже посещённые вершины.
# ─────────────────────────────────────────

def find_path(d):
    path = [(rows-1, 0)]
    visited = {(rows-1, 0)}
    steps = [f"\nВосстановление пути из ({rows-1},0):"]
    r, c = rows-1, 0

    while not (r == 0 and c == cols-1):
        cur = d[r][c]

        # Все возможные соседи с их рёбрами
        candidates = []
        if c + 1 < cols:
            candidates.append((r, c+1, hE[r][c],   "вправо"))
        if c - 1 >= 0:
            candidates.append((r, c-1, hE[r][c-1], "влево"))
        if r - 1 >= 0:
            candidates.append((r-1, c, vE[r-1][c], "вверх"))
        if r + 1 < rows:
            candidates.append((r+1, c, vE[r][c],   "вниз"))

        moved = False
        for nr, nc, w, direction in candidates:
            diff = cur - w
            match = (diff == d[nr][nc])
            steps.append(
                f"  {cur}-{w}={diff} {'==' if match else '!='} d[{nr},{nc}]={d[nr][nc]}  {'✓' if match else '✗'}"
            )
            # Идём в первого подходящего непосещённого соседа
            if match and not moved and (nr, nc) not in visited:
                steps.append(f"  → идём {direction} в ({nr},{nc})")
                r, c = nr, nc
                path.append((r, c))
                visited.add((r, c))
                moved = True

        if not moved:
            steps.append("  ⚠ Не удалось продолжить путь!")
            break

    return path, steps


# ─────────────────────────────────────────
#  начло алгоритммма
# ─────────────────────────────────────────

print("\n" + "=" * 50)
if method == "1":
    print("МЕТОД ФОРДА-БЕЛЛМАНА — пошаговые вычисления")
    print("=" * 50)
    d, steps = ford_bellman()
    method_name = "Форд-Беллман"
else:
    print("МЕТОД МИНТИ — пошаговые вычисления")
    print("=" * 50)
    d, steps = minty()
    method_name = "Минти"

for s in steps:
    print(s)

path, path_steps = find_path(d)
for s in path_steps:
    print(s)

path_str = " → ".join(f"({r},{c})" for r, c in path)
print("\n" + "=" * 50)
print(f"КРАТЧАЙШИЙ ПУТЬ: {path_str}")
print(f"ДЛИНА ПУТИ:      {d[rows-1][0]}")
print("=" * 50)


# ─────────────────────────────────────────
#   ГРАФ
# ─────────────────────────────────────────

path_set = set(path)

def is_path_edge_h(r, c):
    for i in range(len(path)-1):
        r1, c1 = path[i]; r2, c2 = path[i+1]
        if r1 == r2 == r and min(c1, c2) == c and abs(c1-c2) == 1:
            return True
    return False

def is_path_edge_v(r, c):
    for i in range(len(path)-1):
        r1, c1 = path[i]; r2, c2 = path[i+1]
        if c1 == c2 == c and min(r1, r2) == r and abs(r1-r2) == 1:
            return True
    return False

fig, ax = plt.subplots(figsize=(cols*1.8, rows*1.8))
ax.set_aspect('equal')
ax.axis('off')
ax.set_title(f'Метод {method_name}   |   Кратчайший путь = {d[rows-1][0]}',
             fontsize=13, fontweight='bold', pad=15)

def pos(r, c):
    return c * 2, (rows-1-r) * 2

# Рёбра горизонтальные
for r in range(rows):
    for c in range(cols-1):
        x1, y1 = pos(r, c); x2, y2 = pos(r, c+1)
        on_path = is_path_edge_h(r, c)
        ax.plot([x1, x2], [y1, y2],
                color='#c48cff' if on_path else '#cccccc',
                linewidth=3 if on_path else 1.2, zorder=1)
        ax.text((x1+x2)/2, (y1+y2)/2+0.18, str(hE[r][c]),
                ha='center', va='bottom', fontsize=7.5, color='#888888')

# Рёбра вертикальные
for r in range(rows-1):
    for c in range(cols):
        x1, y1 = pos(r, c); x2, y2 = pos(r+1, c)
        on_path = is_path_edge_v(r, c)
        ax.plot([x1, x2], [y1, y2],
                color='#c48cff' if on_path else '#cccccc',
                linewidth=3 if on_path else 1.2, zorder=1)
        ax.text((x1+x2)/2+0.15, (y1+y2)/2, str(vE[r][c]),
                ha='left', va='center', fontsize=7.5, color='#888888')

# Узлы
for r in range(rows):
    for c in range(cols):
        x, y = pos(r, c)
        is_src = (r == 0 and c == cols-1)
        is_dst = (r == rows-1 and c == 0)
        on_p   = (r, c) in path_set

        if is_src:
            color, tc = '#2A6EBB', 'white'
        elif is_dst or on_p:
            color, tc = '#c48cff', 'white'
        else:
            color, tc = '#EEF3FA', '#222222'

        circle = plt.Circle((x, y), 0.38, color=color, zorder=3,
                             linewidth=1.2, ec='#9aaabb')
        ax.add_patch(circle)
        ax.text(x, y, str(d[r][c]),
                ha='center', va='center', fontsize=9,
                fontweight='bold', color=tc, zorder=4)

# Подписи начало / конец
xs, ys = pos(0, cols-1)
xd, yd = pos(rows-1, 0)
ax.text(xs, ys+0.6, 'ЦЕЛЬ\n(0)', ha='center', va='bottom', fontsize=8,
        color='#2A6EBB', fontweight='bold')
ax.text(xd, yd-0.6, f'СТАРТ\n({d[rows-1][0]})', ha='center', va='top', fontsize=8,
        color='#c48cff', fontweight='bold')

# Легенда
legend = [
    mpatches.Patch(color='#2A6EBB', label='Цель (0)'),
    mpatches.Patch(color='#c48cff', label=f'Путь / Старт ({d[rows-1][0]})'),
    mpatches.Patch(color='#EEF3FA', ec='#9aaabb', label='Остальные узлы'),
]
ax.legend(handles=legend, loc= 'lower right', fontsize=5)


plt.tight_layout()
plt.show()