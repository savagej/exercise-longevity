import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import data

st.title('Exercise for Longevity')

vo2 = st.number_input("VO2max", help="Most smartwatches will calculate your VO2max from exercise data (fitbit and apple watch call it your 'cardio fitness'). You can use [this site](https://www.omnicalculator.com/sports/vo2-max-runners?c=GBP&v=y:1,distance:5!km,time:1500!minsec) to calculate your VO2max from a recent 5k race ")
age = st.number_input("age", 18, 80)
sex = st.selectbox("Sex", ('Male', 'Female'))

met = round(vo2 / 3.5)

cutoff = data.full_data[sex][age]

group_index = 0 if met < cutoff[0] else 1 if met <= cutoff[1] else 2 if met <= cutoff[2] else 3 if met <= cutoff[
    3] else 4
group = data.groups[group_index]

vs = " vs "

if st.button("Calculate"):
    st.header(f"You are in the {group} fitness group")

    hazard_ratios = dict()
    for g in range(group_index + 1, len(data.groups)):
        comparison_lookup = f"{group}{vs}{data.groups[g]}"
        hazard_ratio = data.group_comparison[comparison_lookup]
        hazard_ratios[comparison_lookup] = hazard_ratio

    if len(hazard_ratios) > 0:
        # Results tabs
        st.subheader("Comparison to other fitness groups")
        st.write("In the tabs below you can see the different hazard ratios for your fitness group compared to the higher fitness groups")
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
        # Plot
        st.markdown("""---""")
        st.subheader("Comparison to other things that affect early death")
        st.write("This plot shows the comparison to other fitness groups in context of other medical conditions or poor diets")
        fig, ax = plt.subplots()
        ax.set_xlim([1,6])
        x_values = [x[0] for x in hazard_ratios.values()]
        y_values = [1 for x in hazard_ratios.values()]
        ax.stem(x_values, y_values)
        for x, y, label in zip(x_values, y_values, hazard_ratios.keys()):
            plt.annotate(label, xy=(x, y), xytext=(0, 5), textcoords='offset points', ha='center', va='top',
                         rotation=60)

        comorbidities = ([1.21, 1.41, 2.8], [0.66, 0.66, 0.66], ["Hypertension", "Smoking", "Kidney Failure"])
        ax.stem(comorbidities[0], comorbidities[1], linefmt='C1-')
        for x, y, label in zip(*comorbidities):
            plt.annotate(label, xy=(x, y), xytext=(0, 5), textcoords='offset points', ha='center', va='top',
                         rotation=60)

        diet = ([1.16, 1.45], [0.33, 0.33], ["Too much sugar", "Too much sat. fat"])
        ax.stem(diet[0], diet[1], linefmt='C2-')
        for x, y, label in zip(*diet):
            plt.annotate(label, xy=(x, y), xytext=(0, 5), textcoords='offset points', ha='center', va='top',
                         rotation=60)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.get_yaxis().set_ticks([])
        st.pyplot(fig)
        st.caption("Blue bars show the hazard ratios for your fitness group compared to the higher fitness groups. Orange bars show other medical conditions seen in the study population. Green bars show hazard ratios for bad diets in a different study for a reference.")
        st.caption("Other medical conditions data is from the same study, diet data comes from [this paper](https://www.bmj.com/lookup/doi/10.1136/bmj.m688) and so is not as directly comparable (different population etc.)")
    else:
        st.write("Congrats, keep up the good work")
