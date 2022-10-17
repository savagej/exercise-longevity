import streamlit as st
import plotly.express as px
import data

st.title('Exercise for Longevity')

vo2 = st.number_input("VO2max", help="this is helpful")
age = st.number_input("age", 18, 80)
sex = st.selectbox("Sex", ('Male', 'Female'))

met = round(vo2 / 3.5)

cutoff = data.full_data[sex][age]

group_index = 0 if met < cutoff[0] else 1 if met <= cutoff[1] else 2 if met <= cutoff[2] else 3 if met <= cutoff[
    3] else 4
group = data.groups[group_index]

vs = " vs "

if st.button("Calculate"):
    st.write(f"{met} from {age} {sex}: You are in the {group} group")

    hazard_ratios = dict()
    for g in range(group_index + 1, len(data.groups)):
        comparison_lookup = f"{group}{vs}{data.groups[g]}"
        hazard_ratio = data.group_comparison[comparison_lookup]
        hazard_ratios[comparison_lookup] = hazard_ratio

    if len(hazard_ratios) > 0:
        tabs = st.tabs(hazard_ratios.keys())
        for (t, hr) in zip(tabs, hazard_ratios.keys()):
            with t:
                val, min_, max_ = hazard_ratios[hr]
                percent = int((val - 1) * 100)
                odds = val / (1 + val)
                prob = odds / (1 - odds)
                left, right = hr.split(vs)
                st.write(
                    f"People in {left} group were {round(val, 2)} times more likely to have an early death compared to {right} group")
                # st.write(f"People in {hr} groups had {int(odds * 100)}%  chance of an early death -> prob = {round(prob, 2)}")
    else:
        st.write("Congrats, keep up the good work")
