import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import data

st.title('Exercise for Longevity')
st.write("""
IN 2018 a [study was published](https://doi.org/10.1001/jamanetworkopen.2018.3605) which looked at the the association 
between fitness and long-term mortality. Between 1991 and 2014, they examined over 120,000 patients at 
Cleveland Clinic, determining their fitness levels and noting their age, sex and relevant conditions e.g. smoking, diabetes. 
The patients were then tracked for the rest of the study (on average for 8.5 years). 11% of these patients died in the 23 years 
of the study, which allowed the authors to examine the different risk levels for various levels of fitness and compare
them to the other conditions the patients had.

The patients were bucketed into 4 fitness levels for each sex and age group, `Low`, `Below Average`, `Above Average`, and `High`.
The `High` group was subdivided again, with the very top 2.4% of patients getting put in the `Elite` group.


""")
df_groups = pd.DataFrame([25,25,25,22.6,2.4], columns=["percentile"])
df_groups["_"] = "_"
df_groups["fitness_group"] = data.groups
st.plotly_chart(px.bar(
    df_groups, x="percentile", y="_",
    color="fitness_group", orientation="h",
    hover_name="fitness_group",
    hover_data={"percentile": False, "_": False,  "fitness_group": False},
))
st.write("""
Unsurprisingly there was a negative correlation between the fitness groups and death during the study, but the size 
of the difference was shocking to me, with almost 25% of the `Low` group dying during the study compared to only 5% of 
the `High` group.  
The authors were able to calculate the relative risk of being in one fitness group vs another, and compared this risk 
to the other conditions present in the patient e.g. diabetes, smoking, or kidney failure. At all levels, the 
increased level of mortality compared to the fitness levels above was similar to or greater than these diseases we worry 
a lot about. 

As a doctor focused on Longevity has said [on twitter](https://twitter.com/PeterAttiaMD/status/1499408138658668544) based on his
reading of this study our first,second, and third priorities for longevity should be on well formulated exercise to increase our fitness

""")

with st.sidebar:
    st.header("Title")
    st.write("Enter your details below to calculate your fitness group")
    vo2 = st.number_input("VO2max", help="Most smartwatches will calculate your VO2max from exercise data (fitbit and apple watch call it your 'cardio fitness'). You can use [this site](https://www.omnicalculator.com/sports/vo2-max-runners?c=GBP&v=y:1,distance:5!km,time:1500!minsec) to calculate your VO2max from a recent 5k race ")
    age = st.number_input("age", 18, 80)
    sex = st.selectbox("Sex", ('Male', 'Female'))
    butt = st.button("Calculate")

met = round(vo2 / 3.5, 2)

cutoff = data.full_data[sex][age]

group_index = 0 if met < cutoff[0] else 1 if met <= cutoff[1] else 2 if met <= cutoff[2] else 3 if met <= cutoff[
    3] else 4
group = data.groups[group_index]

vs = " vs "

if butt:
    st.header(f"You are in the {group} fitness group")
    cutoffs_in_vo2 = [v*3.5 for v in cutoff]
    diffs = []
    for i,v in enumerate(cutoffs_in_vo2):
        if i == 0:
            diffs.append(v)
        else:
            diffs.append(v - cutoffs_in_vo2[i-1])
    df_cutoff = pd.DataFrame([cutoffs_in_vo2, diffs], index=["vO2max_cutoff", "VO2max"]).T
    df_cutoff["_"] = "_"
    df_cutoff["fitness_group"] = data.groups[:-1]
    px_fig = px.bar(
        df_cutoff, x="VO2max", y="_",
        color="fitness_group", orientation="h",
        hover_name="fitness_group", hover_data={"VO2max": False, "_": False, "vO2max_cutoff": True, "fitness_group": True},
        range_x=(15, max(16.2*3.5, vo2+10))
    )
    px_fig.add_vline(vo2, annotation_text="Your vo2max")
    px_fig.update_yaxes(visible=False)
    st.plotly_chart(px_fig)
    st.caption(f"Your VO2max of {vo2} in relation to the four largest groups in the study. Any VO2max higher than the 'High' group is the 'Elite' group, which made up the top 2.4% of study participants")

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
