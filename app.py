import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import data

st.set_page_config(
    page_title="Exercise for longevity",
    page_icon=":runner:",
    menu_items={"Report a Bug": "mailto:john@johnsavage.net", "Get help": None, "About": "Made by John Savage 2022. Contact: john@johnsavage.net"}
)

st.title('Exercise for Longevity')
st.write("""
This website is an attempt to highlight how much impact exercise can have on our health and longevity when compared
to any other variable within our control like our diet and smoking, or when compared to common chronic diseases.

The intent is not to add an additional worry about our lifestyle choices, but to show that if we only have time or 
headspace to focus on one aspect of our life for longevity, consistent and enjoyable exercise should be the majority of people's focus.

This is all based on an interesting study which you can learn about in the panel at the bottom of the page, 
but you can simply enter your details in the form to find out your fitness group and comparisons between the relative risk of your fitness group with others.
""")

with st.expander("Input", expanded=True):
    st.header("What fitness group are you in?")
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
    st.plotly_chart(px_fig, use_container_width=True)
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

        df_other_hazard_ratios = pd.DataFrame(data.other_hazard_ratios, columns=["hazard_ratio", "name", "type", "err_low", "err_high"])
        df_exercise = pd.DataFrame(zip(
            [x[0] for x in hazard_ratios.values()],
            hazard_ratios.keys(),
            ["fitness" for x in hazard_ratios.values()],
            [x[1] for x in hazard_ratios.values()],
            [x[2] for x in hazard_ratios.values()],
        ), columns=["hazard_ratio", "name", "type", "err_low", "err_high"])

        df_plot = pd.concat([df_other_hazard_ratios, df_exercise])
        df_plot["err_plus"] = df_plot["err_high"] - df_plot["hazard_ratio"]
        df_plot["err_minus"] = df_plot["hazard_ratio"] - df_plot["err_low"]

        fig2 = px.scatter(df_plot, x="hazard_ratio", y="name", color="type",
                            # title="Gender Earnings Disparity",
                            labels={"hazard_ratio": "Increase in likelihood of early death", "name": "Risks", "type":"Risk type"},
                            error_x="err_plus",
                            error_x_minus="err_minus"
                          )
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("Other medical conditions data is from the same study, diet data comes from [this paper](https://www.bmj.com/lookup/doi/10.1136/bmj.m688) and so is not as directly comparable (different population etc.)")

        if group == "High":
            st.write("Your group were already the highest 25% of people in the study, but even so it is clear that continuing to increase fitness levels to `Elite` levels produces longevity benefits, though the error bars are quite large.")
        elif group == "Above Average":
            st.write("For example, comparing your group to those in the `High` fitness group, the changed risk of mortality is comparable to smoking, diabetes, high saturated fat or very low fibre diets")
        elif group == "Below Average":
            st.write("For example, comparing your group to those in the `Above Average` fitness group, the changed risk of mortality is comparable to smoking, diabetes, high saturated fat or very low fibre diets")
        elif group == "Low":
            st.write("For example, comparing your group to those in the `Below Average` fitness group, the changed risk of mortality is greater than that of smoking, diabetes, high saturated fat or very low fibre diets")
            st.write("Comparing to the `Above Average` fitness group, the changed risk of mortality is comparable to Kidney Failure (End stage renal disease, when the kidneys completely stop working and require transplants)")
            st.write("People in the `High` fitness group were almost 4 times less likely to die during the study than the `Low` group")
        st.subheader("What's next")
        st.write("Missing a way to help understand how much exercise and of what type will result in a given fitness bucket.")
        st.write("""
        The recommendation for how much exercise per week by longevity experts is exercise at a "conversational" level, your breathing should be faster, but you could easily hold a conversation with someone.
    - For a beginner: ~2 hours a week is a good place to start
    - Ideally: 3-4 hours per week 
    """)
    else:
        st.write("Congrats, keep up the good work")

with st.expander("Expand for background"):
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
    df_groups = pd.DataFrame([25, 25, 25, 22.6, 2.4], columns=["percentile"])
    df_groups["_"] = "_"
    df_groups["fitness_group"] = data.groups
    st.plotly_chart(px.bar(
        df_groups, x="percentile", y="_",
        color="fitness_group", orientation="h",
        hover_name="fitness_group",
        hover_data={"percentile": False, "_": False, "fitness_group": False},
    ), use_container_width=True)
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
