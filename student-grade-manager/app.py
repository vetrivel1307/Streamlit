
import streamlit as st
import pandas as pd

# ---------------------------------
# PAGE CONFIGURATION
# ---------------------------------

st.set_page_config(
    page_title="Student Grade Manager",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------
# CUSTOM CSS
# ---------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #f4f7fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    .hero {
        background: linear-gradient(120deg, #142b4a, #245b91);
        padding: 32px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        font-size: 34px;
        margin-bottom: 8px;
    }

    .hero p {
        color: #dce8f5;
        font-size: 16px;
        margin-bottom: 0;
    }

    .section-title {
        color: #183451;
        font-size: 22px;
        font-weight: 700;
        margin: 12px 0 16px 0;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #e4eaf2;
        padding: 18px;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(20, 43, 74, 0.04);
    }

    div[data-testid="stMetricLabel"] {
        color: #65758b;
    }

    div[data-testid="stMetricValue"] {
        color: #183451;
        font-weight: 700;
    }

    div[data-testid="stForm"] {
        background: white;
        padding: 22px;
        border: 1px solid #e4eaf2;
        border-radius: 14px;
    }

    .stButton button,
    .stDownloadButton button {
        border-radius: 9px;
        font-weight: 600;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------
# SESSION STORAGE
# ---------------------------------

if "students" not in st.session_state:
    st.session_state.students = []


# ---------------------------------
# GRADE CALCULATION
# ---------------------------------

def calculate_grade(mark):

    if 90 <= mark <= 100:
        return "A"
    elif 80 <= mark < 90:
        return "B"
    elif 70 <= mark < 80:
        return "C"
    elif 60 <= mark < 70:
        return "D"
    else:
        return "E"


# ---------------------------------
# HEADER
# ---------------------------------

st.markdown("""
<div class="hero">
    <h1>🎓 Student Grade Manager</h1>
    <p>Manage student performance, calculate grades
    and monitor class results in one place.</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------
# ADD STUDENT SECTION
# ---------------------------------

st.markdown(
    '<div class="section-title">➕ Add New Student</div>',
    unsafe_allow_html=True
)

with st.container(border=True):

    with st.form("student_form", clear_on_submit=True):

        col1, col2 = st.columns([2, 1])

        with col1:
            name = st.text_input(
                "Student Name",
                placeholder="Enter student name"
            )

        with col2:
            mark = st.number_input(
                "Student Mark",
                min_value=0,
                max_value=100,
                value=0,
                step=1
            )

        submitted = st.form_submit_button(
            "Add Student",
            type="primary",
            use_container_width=True
        )

        if submitted:

            name = name.strip()

            if not name:
                st.error("Please enter a student name.")

            else:

                student = {
                    "Name": name,
                    "Mark": int(mark),
                    "Grade": calculate_grade(int(mark))
                }

                st.session_state.students.append(student)

                st.success(
                    f"Student {name} added successfully!"
                )

                st.rerun()


# ---------------------------------
# CLASS STATISTICS
# ---------------------------------

students = st.session_state.students

st.markdown(
    '<div class="section-title">📊 Class Overview</div>',
    unsafe_allow_html=True
)

if students:

    marks = [student["Mark"] for student in students]

    total_students = len(students)
    average = sum(marks) / total_students
    highest = max(marks)
    lowest = min(marks)

else:

    total_students = 0
    average = 0
    highest = 0
    lowest = 0


col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", total_students)
col2.metric("Class Average", f"{average:.2f}")
col3.metric("Highest Mark", highest)
col4.metric("Lowest Mark", lowest)


# ---------------------------------
# STUDENT RESULTS
# ---------------------------------

st.markdown(
    '<div class="section-title">📋 Student Results</div>',
    unsafe_allow_html=True
)

if students:

    df = pd.DataFrame(students)

    # Search and filter
    filter_col1, filter_col2 = st.columns([2, 1])

    with filter_col1:

        search_name = st.text_input(
            "Search Student",
            placeholder="Type a student name..."
        )

    with filter_col2:

        selected_grade = st.selectbox(
            "Filter by Grade",
            ["All Grades", "A", "B", "C", "D", "E"]
        )

    filtered_df = df.copy()

    if search_name:

        filtered_df = filtered_df[
            filtered_df["Name"].str.contains(
                search_name,
                case=False,
                na=False
            )
        ]

    if selected_grade != "All Grades":

        filtered_df = filtered_df[
            filtered_df["Grade"] == selected_grade
        ]

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Showing {len(filtered_df)} of {total_students} student records."
    )

    # ---------------------------------
    # GRADE DISTRIBUTION
    # ---------------------------------

    st.markdown(
        '<div class="section-title">📈 Grade Distribution</div>',
        unsafe_allow_html=True
    )

    grade_order = ["A", "B", "C", "D", "E"]

    grade_counts = (
        df["Grade"]
        .value_counts()
        .reindex(grade_order, fill_value=0)
    )

    chart_col, detail_col = st.columns([3, 2])

    with chart_col:

        chart_data = pd.DataFrame({
            "Students": grade_counts
        })

        st.bar_chart(chart_data)

    with detail_col:

        st.markdown("#### Grade Breakdown")

        for grade in grade_order:

            count = int(grade_counts[grade])

            percentage = (
                count / total_students * 100
                if total_students else 0
            )

            st.write(
                f"**Grade {grade}** — {count} students "
                f"({percentage:.1f}%)"
            )

    # ---------------------------------
    # DOWNLOAD STUDENT RECORDS
    # ---------------------------------

    st.markdown(
        '<div class="section-title">⬇️ Export Records</div>',
        unsafe_allow_html=True
    )

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Student Records (CSV)",
        data=csv_data,
        file_name="student_results.csv",
        mime="text/csv",
        type="primary"
    )

else:

    st.info(
        "No student records yet. Add your first student using the form above."
    )


# ---------------------------------
# FOOTER
# ---------------------------------

st.markdown("---")

st.markdown(
    "<center>Student Grade Manager | Built with Python & Streamlit</center>",
    unsafe_allow_html=True
)
