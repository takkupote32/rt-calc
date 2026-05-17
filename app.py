import streamlit as st

# ページ全体の基本設定（ダークモード風のスタイル調整用）
st.set_page_config(
    page_title="放射線治療 診療報酬シミュレーター 2026",
    page_icon="⚛️",
    layout="wide"
)

# 簡易計算機のロジック用セッション状態初期化
if "calc_expr" not in st.session_state:
    st.session_state.calc_expr = ""
if "calc_display" not in st.session_state:
    st.session_state.calc_display = "0"

# --- 簡易計算機関数の定義 ---
def press_calc(char):
    if char == "C":
        st.session_state.calc_expr = ""
        st.session_state.calc_display = "0"
    elif char == "⌫":
        if "Error" in st.session_state.calc_display:
            st.session_state.calc_expr = ""
            st.session_state.calc_display = "0"
        else:
            st.session_state.calc_expr = st.session_state.calc_expr[:-1]
            st.session_state.calc_display = st.session_state.calc_expr if st.session_state.calc_expr else "0"
    elif char == "=":
        try:
            if st.session_state.calc_expr:
                # 簡易的な四則演算評価
                result = str(eval(st.session_state.calc_expr))
                if result.endswith(".0"):
                    result = result[:-2]
                try:
                    st.session_state.calc_display = f"{float(result):,.0f}" if result.replace(".","",1).isdigit() else result
                except:
                    st.session_state.calc_display = result
                st.session_state.calc_expr = result
        except ZeroDivisionError:
            st.session_state.calc_display = "Error: 0除算"
            st.session_state.calc_expr = ""
        except:
            st.session_state.calc_display = "Error"
            st.session_state.calc_expr = ""
    else:
        if "Error" in st.session_state.calc_display:
            st.session_state.calc_expr = ""
        
        if st.session_state.calc_expr == "" and char.isdigit() and char != "0":
            st.session_state.calc_expr = str(char)
        else:
            st.session_state.calc_expr += str(char)
        st.session_state.calc_display = st.session_state.calc_expr

# --- サイドバー：照射方法選択 ＆ 計算機 ---
with st.sidebar:
    st.header("🧮 ツールメニュー")
    
    # 1. 簡易計算機（アコーディオン）
    with st.expander("🧮 簡易計算機を開く", expanded=False):
        st.subheader(f"Display: {st.session_state.calc_display}")
        
        # ボタン配置用のグリッド
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("C", key="c_C"): press_calc("C")
        if c2.button("⌫", key="c_B"): press_calc("⌫")
        if c3.button("/", key="c_D"): press_calc("/")
        if c4.button("*", key="c_M"): press_calc("*")
        
        if c1.button("7", key="c_7"): press_calc("7")
        if c2.button("8", key="c_8"): press_calc("8")
        if c3.button("9", key="c_9"): press_calc("9")
        if c4.button("-", key="c_S"): press_calc("-")
        
        if c1.button("4", key="c_4"): press_calc("4")
        if c2.button("5", key="c_5"): press_calc("5")
        if c3.button("6", key="c_6"): press_calc("6")
        if c4.button("+", key="c_A"): press_calc("+")
        
        if c1.button("1", key="c_1"): press_calc("1")
        if c2.button("2", key="c_2"): press_calc("2")
        if c3.button("3", key="c_3"): press_calc("3")
        if c4.button("=", key="c_E"): press_calc("=")
        
        if c1.button("0", key="c_0"): press_calc("0")
        if c2.button(".", key="c_P"): press_calc(".")

    st.markdown("---")
    st.subheader("照射方法を選択")
    methods = [
        "前立腺VMAT", "全乳房(一連)", "IMRT", "1門照射", 
        "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "全身照射TBI", 
        "緩和寡分割", "ケロイド", "肺定位SBRT", "脳定位SRT"
    ]
    # デフォルトを「前立腺VMAT」に
    selected_method = st.radio("メニュー", methods, index=0, label_visibility="collapsed")

# --- メインコンテンツ ---
st.title("⚛️ 放射線治療 診療報酬シミュレーター 2026")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 基本入力エリア")
    
    # 負担割合
    ratio_str = st.segmented_control("患者負担割合", ["1割", "2割", "3割"], default="3割")
    ratio = int(ratio_str.replace("割", "")) if ratio_str else 3

    # 患者区分（脳定位SRTの場合は自動で入院にする制御を考慮）
    default_patient_idx = 1 if selected_method == "脳定位SRT" else 0
    patient_type = st.radio("患者区分", ["外来", "入院"], index=default_patient_idx, horizontal=True)

    # IGRT区分 (表示制御用)
    no_igrt_list = [
        "1門照射", "対向2門", "非対向2門・3門照射", "ケロイド", "全乳房(一連)",
        "前立腺VMAT", "肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"
    ]
    
    if selected_method not in no_igrt_list:
        default_igrt_idx = 3 if selected_method == "IMRT" else 0
        igrt_selection = st.selectbox("IGRT区分", ["なし", "イ.体表", "ロ.骨構造", "ハ.腫瘍"], index=default_igrt_idx)
    else:
        igrt_selection = "なし"

    # 動的フレーム要素のシミュレート
    grid_fix_list = ["前立腺VMAT", "IMRT", "1門照射", "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "ケロイド"]
    default_fix = "作成あり" if selected_method == "前立腺VMAT" else "なし"
    fix_var = "なし"
    if selected_method in grid_fix_list:
        fix_var = st.segmented_control("体外照射用固定器具", ["なし", "作成あり"], default=default_fix)

    breath_var = "なし"
    if selected_method in ["IMRT", "肺定位SBRT", "全乳房(一連)"]:
        breath_var = st.segmented_control("呼吸性移動対策", ["なし", "あり"], default="なし")

    breast_igrt_var = "なし"
    if selected_method == "全乳房(一連)":
        breast_igrt_var = st.segmented_control("IGRT(一連2400点)", ["なし", "あり"], default="なし")

    # 回数入力の制御
    one_series_methods = ["前立腺VMAT", "全乳房(一連)", "肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"]
    outpatient_add_series = ["前立腺VMAT", "全乳房(一連)", "肺定位SBRT", "脳定位SRT", "緩和寡分割"]

    count = 0
    if selected_method not in one_series_methods or (selected_method in outpatient_add_series and patient_type == "外来"):
        lbl_text = "外来治療回数 (加算用):" if selected_method in one_series_methods else "合計照射回数:"
        count = st.number_input(lbl_text, min_value=0, value=1, step=1)
    
    if selected_method in one_series_methods:
        st.info(f"💡 {selected_method} は一連算定項目です")

# --- 計算ロジック本体 (左側ベース用) ---
def calculate_base():
    formula = []
    total_pts = 0
    exclude_m000 = ["肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"]
    
    if selected_method in exclude_m000:
        formula.append("・管理料(M000): 0点 (一連に含む)")
    else:
        if selected_method in ["1門照射", "ケロイド", "対向2門"]: 
            m000_pts = 2700
        elif selected_method == "非対向2門・3門照射":
            m000_pts = 3100
        elif "IMRT" in selected_method or "VMAT" in selected_method: 
            m000_pts = 5000
        elif selected_method == "全乳房(一連)":
            m000_pts = 4000
        else: 
            m000_pts = 4000
            
        total_pts += m000_pts
        formula.append(f"・管理料(M000): {m000_pts:,}点")
        total_pts += 330
        formula.append("・放射線治療専任加算: 330点")

    total_pts += 1100
    formula.append("・安全管理料2: 1,100点")
    if fix_var == "作成あり":
        total_pts += 1000
        formula.append("・体外照射用固定器具加算: 1,000点")

    if selected_method in one_series_methods:
        if selected_method == "肺定位SBRT":
            total_pts += 63000
            formula.append("・定位照射(一連): 63,000点")
            if breath_var == "あり":
                total_pts += 5000
                formula.append("・呼吸性移動対策加算: 5,000点")
        elif selected_method == "脳定位SRT":
            total_pts += 63000
            formula.append("・定位照射(一連): 63,000点")
        elif selected_method == "前立腺VMAT":
            total_pts += (96500 + 9000)
            formula.append("・照射料(一連): 96,500点\n・IGRT(ハ.腫瘍 一連): 9,000点")
        elif selected_method == "全乳房(一連)":
            total_pts += 41500
            formula.append("・照射料(一連): 41,500点")
            if breast_igrt_var == "あり":
                total_pts += 2400
                formula.append("・IGRT(一連): 2,400点")
            if breath_var == "あり":
                total_pts += 2400
                formula.append("・呼吸性移動対策加算(一連): 2,400点")
        elif selected_method == "全身照射TBI":
            total_pts += 30000
            formula.append("・全身照射(一連): 30,000点")
        elif selected_method == "緩和寡分割":
            total_pts += 8000
            formula.append("・緩和寡分割(一連): 8,000点")
        
        if patient_type == "外来" and selected_method in outpatient_add_series:
            outpatient_pts = count * 100
            total_pts += outpatient_pts
            formula.append(f"・外来放射線治療加算(100点) × {count}回: {outpatient_pts:,}点")
    else:
        if selected_method == "IMRT": base = 3000
        elif "4門以上・運動・原体照射" in selected_method: base = 1750
        elif selected_method in ["対向2門", "非対向2門・3門照射"]: base = 1750
        elif selected_method in ["1門照射", "ケロイド"]: base = 840
        else: base = 0
        
        igrt_map = {"なし": 0, "イ.体表": 150, "ロ.骨構造": 300, "ハ.腫瘍": 450}
        igrt_pts = igrt_map.get(igrt_selection, 0)

        breath_per_shot = 0
        if selected_method == "IMRT" and breath_var == "あり":
            breath_per_shot = 150
    
        total_pts += (base + igrt_pts + breath_per_shot) * count
        formula.append(f"・照射料({base}点) × {count}回: {base * count:,}点")
        if igrt_pts > 0:
            formula.append(f"・IGRT({igrt_pts}点) × {count}回: {igrt_pts * count:,}点")
        if breath_per_shot > 0:
            formula.append(f"・呼吸性移動対策({breath_per_shot}点) × {count}回: {breath_per_shot * count:,}点")
            
        if patient_type == "外来" and selected_method != "ケロイド":
            outpatient_pts = count * 100
            total_pts += outpatient_pts
            formula.append(f"・外来放射線治療加算(100点) × {count}回: {outpatient_pts:,}点")

    final_pay = total_pts * 10 * (ratio / 10)
    return total_pts, final_pay, formula

base_pts, final_pay, formula_list = calculate_base()

with col2:
    st.subheader("💰 会計計算結果")
    st.metric(label="概算窓口負担額", value=f"¥ {final_pay:,.0f}")
    
    # 計算内訳の表示
    full_formula_text = "\n".join(formula_list) + f"\n----------------------------\n合計点数: {base_pts:,} 点\n計算式: {base_pts:,}点 × 10円 × {ratio/10} = ¥{final_pay:,.0f}"
    st.text_area("計算内訳明細", value=full_formula_text, height=180)
    
    st.warning("⚠️ ※外来の場合、「外来放射線診療料（診察代）」が別途加算されます。\n\n※治療の進行状況やプラン変更により実際と異なる場合があります。")

st.markdown("---")

# --- 追加・変更シミュレーションエリア ---
is_expanded = st.checkbox("追加・変更分のシミュレーションを開く ≫")

if is_expanded:
    st.header("🔄 追加・変更シミュレーション")
    
    ex_col1, ex_col2 = st.columns([1, 1])
    
    with ex_col1:
        check_extra_2 = st.checkbox("2回目の計算として実行する (2回目会計)", value=False)
        
        extra_methods_1st = [
            "前立腺VMAT", "全乳房(一連)", "IMRT", "1門照射", 
            "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "ケロイド",
            "肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"
        ]
        extra_methods_2nd = ["1門照射", "対向2門", "非対向2門・3門照射", "4門以上・運動・原体照射", "ケロイド"]
        
        if check_extra_2:
            st.subheader("追加する照射方法 (2回目)")
            selected_extra_method = st.selectbox("照射方法", extra_methods_2nd, key="ex_method_2")
            extra_count = st.number_input("2回目 照射回数:", min_value=0, value=1, step=1, key="ex_count_2")
            extra_igrt = "なし" # 2回目はなし固定
        else:
            st.subheader("追加する照射方法 (1回目)")
            selected_extra_method = st.selectbox("照射方法", extra_methods_1st, key="ex_method_1")
            
            # 一連算定項目の場合は回数固定の制御
            if selected_extra_method in one_series_methods:
                st.disabled_text = st.text_input("1回目 照射回数:", value="1 (一連算定のため固定)", disabled=True)
                extra_count = 1
            else:
                extra_count = st.number_input("1回目 照射回数:", min_value=0, value=1, step=1, key="ex_count_1")
            
            if selected_extra_method not in no_igrt_list:
                extra_igrt = st.selectbox("1回目 IGRT区分", ["なし", "イ.体表", "ロ.骨構造", "ハ.腫瘍"], key="ex_igrt_1")
            else:
                extra_igrt = "なし"

    # 追加分の点数計算ロジック
    def get_extra_points(method, count, igrt_selection, is_second):
        formula_list_ex = []
        if is_second:
            pts_map = {"1門照射": 336, "対向2門": 700, "非対向2門・3門照射": 700, "4門以上・運動・原体照射": 700, "ケロイド": 336}
        else:
            pts_map = {
                "前立腺VMAT": 96500 + 9000, "全乳房(一連)": 41500, "IMRT": 3000, "1門照射": 840, "ケロイド": 840,
                "対向2門": 1750, "非対向2門・3門照射": 1750, "4門以上・運動・原体照射": 1750, "肺定位SBRT": 63000,
                "脳定位SRT": 63000, "全身照射TBI": 30000, "緩和寡分割": 8000
            }
        
        extra_base_pts = pts_map.get(method, 0)
        extra_total_pts = 0
        
        exclude_m000 = ["肺定位SBRT", "脳定位SRT", "全身照射TBI", "緩和寡分割"]
        if method in exclude_m000:
            formula_list_ex.append("・追加管理料(M000): 0点 (一連に含むため算定不可)")
        else:
            if method in ["1門照射", "ケロイド", "対向2門"]: m000_pts = 2700
            elif method == "非対向2門・3門照射": m000_pts = 3100
            elif "IMRT" in method or "VMAT" in method: m000_pts = 5000
            elif method == "全乳房(一連)": m000_pts = 4000
            else: m000_pts = 4000
            
            extra_total_pts += (m000_pts + 330)
            formula_list_ex.append(f"・追加管理料(M000): {m000_pts:,}点\n・追加放射線治療専任加算: 330点")

        if method in one_series_methods:
            extra_total_pts += extra_base_pts
            if method == "前立腺VMAT":
                formula_list_ex.append("・追加照射(前立腺VMAT 一連): 96,500点\n・追加IGRT(ハ.腫瘍 一連): 9,000点")
            else:
                prefix = "2回目" if is_second else "追加"
                formula_list_ex.append(f"・{prefix}照射({method}): {extra_base_pts:,}点")
        else:
            igrt_map = {"なし": 0, "イ.体表": 150, "ロ.骨構造": 300, "ハ.腫瘍": 450}
            extra_igrt_pts = igrt_map.get(igrt_selection, 0)
            
            shot_pts = extra_base_pts * count
            extra_total_pts += shot_pts
            
            prefix = "2回目" if is_second else "追加"
            formula_list_ex.append(f"・{prefix}照射({method}): {extra_base_pts:,}点 × {count}回 = {shot_pts:,}点")
            
            if extra_igrt_pts > 0:
                igrt_total_pts = extra_igrt_pts * count
                extra_total_pts += igrt_total_pts
                formula_list_ex.append(f"・追加IGRT({igrt_selection} {extra_igrt_pts}点) × {count}回 = {igrt_total_pts:,}点")

        if not is_second and patient_type == "外来" and method != "ケロイド" and method not in one_series_methods:
            extra_outpatient_pts = count * 100
            extra_total_pts += extra_outpatient_pts
            formula_list_ex.append(f"・追加外来放射線治療加算(100点) × {count}回: {extra_outpatient_pts:,}点")

        return extra_total_pts, formula_list_ex

    extra_pts, extra_formula_list = get_extra_points(selected_extra_method, extra_count, extra_igrt, check_extra_2)
    extra_pay = extra_pts * 10 * (ratio / 10)

    # 総合計計算
    grand_total_pts = base_pts + extra_pts
    grand_final_pay = grand_total_pts * 10 * (ratio / 10)

    with ex_col2:
        title_prefix = "▼ 2回目" if check_extra_2 else "▼ 1回目"
        st.subheader(f"{title_prefix}追加分のみの計算結果")
        st.metric(label="追加分概算金額", value=f"¥ {extra_pay:,.0f}")
        
        ex_full_txt = "\n".join(extra_formula_list) + f"\n----------------------------\n追加点数: {extra_pts:,} 点\n計算式: {extra_pts:,}点 × 10円 × {ratio/10} = ¥{extra_pay:,.0f}"
        st.text_area("追加分内訳明細", value=ex_full_txt, height=120, key="ex_text_area")
        
        # 総合計の大きなカード風表示
        st.markdown("---")
        if check_extra_2:
            st.success("#### 🟩 【左側会計 ＋ 2回目会計】総合計 (窓口負担額)")
            st.write(f"### **¥ {grand_final_pay:,.0f}** （概算）")
            st.info(f"総点数: {grand_total_pts:,} 点  \n(治療ベース: {base_pts:,}点 + 2回目追加: {extra_pts:,}点)")
        else:
            st.success("#### 🟩 差額合算後の総合計 (窓口負担額)")
            st.write(f"### **¥ {grand_final_pay:,.0f}** （概算）")
            st.info(f"総点数: {grand_total_pts:,} 点  \n(治療ベース: {base_pts:,}点 + 1回目追加: {extra_pts:,}点)")
