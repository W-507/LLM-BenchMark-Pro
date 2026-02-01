import streamlit as st
import pandas as pd
import glob
import os
import altair as alt

st.set_page_config(page_title="LLM-BenchMark-Pro", layout="wide")

st.title("LLM-BenchMark-Pro Dashboard")

# sidebar for configuration
st.sidebar.header("Configuration")
results_files = glob.glob("results_*.csv")
if not results_files:
    st.warning("No benchmark results found. Run `python main.py` first.")
else:
    selected_file = st.sidebar.selectbox("Select Results File", results_files)
    
    if selected_file:
        df = pd.read_csv(selected_file)
        
        # Key Metrics
        st.header("Key Performance Indicators")
        col1, col2, col3 = st.columns(3)
        
        avg_ttft = df['ttft'].mean()
        avg_tps = df['tps'].mean()
        total_cost = df['cost'].sum()
        
        col1.metric("Avg TTFT (s)", f"{avg_ttft:.4f}")
        col2.metric("Avg TPS", f"{avg_tps:.2f}")
        col3.metric("Total Cost ($)", f"{total_cost:.4f}")
        
        # Charts
        st.header("Comparative Analysis")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Efficiency Frontier", "Latency vs Cost", "Throughput", "Raw Data"])
        
        with tab1:
            st.subheader("Efficiency Frontier (Quality vs Cost)")
            if 'quality_score' in df.columns:
                chart_eff = alt.Chart(df).mark_circle(size=100).encode(
                    x=alt.X('cost', title='Cost ($)'),
                    y=alt.Y('quality_score', title='Quality Score'),
                    color='model',
                    tooltip=['model', 'cost', 'quality_score', 'ttft']
                ).interactive()
                st.altair_chart(chart_eff, use_container_width=True)
                st.info("Top-Left models are more efficient (High Quality, Low Cost).")
            else:
                st.warning("Quality scores not available. Run main.py with evaluation enabled.")

        with tab2:
            st.subheader("Total Latency vs Cost")
            chart = alt.Chart(df).mark_circle(size=100).encode(
                x='total_latency',
                y='cost',
                color='model',
                tooltip=['model', 'total_latency', 'cost', 'ttft']
            ).interactive()
            st.altair_chart(chart, use_container_width=True)
            
        with tab2:
            st.subheader("Tokens Per Second (TPS)")
            chart_tps = alt.Chart(df).mark_bar().encode(
                x='model',
                y='tps',
                color='model',
                tooltip=['model', 'tps']
            ).interactive()
            st.altair_chart(chart_tps, use_container_width=True)
            
        with tab3:
            st.dataframe(df)

            # Export Options
            st.subheader("Export Report")
            col1, col2 = st.columns(2)
            
            csv = df.to_csv(index=False).encode('utf-8')
            col1.download_button(
                "Download CSV",
                csv,
                "benchmark_report.csv",
                "text/csv",
                key='download-csv'
            )
            
            # Excel export
            import io
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            
            col2.download_button(
                label="Download Excel",
                data=buffer,
                file_name="benchmark_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # PDF Export
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet

            def create_pdf(dataframe):
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
                elements = []
                styles = getSampleStyleSheet()
                
                elements.append(Paragraph("LLM-BenchMark-Pro Report", styles['Title']))
                elements.append(Paragraph("Performance Summary", styles['Heading2']))
                
                # Summary Stats
                stats = [
                    ["Metric", "Value"],
                    ["Avg TTFT", f"{dataframe['ttft'].mean():.4f} s"],
                    ["Avg TPS", f"{dataframe['tps'].mean():.2f}"],
                    ["Total Cost", f"${dataframe['cost'].sum():.4f}"]
                ]
                t = Table(stats)
                t.setStyle(TableStyle([('BACKGROUND', (0, 0), (1, 0), colors.grey),
                                       ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
                                       ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                       ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                       ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                       ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
                elements.append(t)
                
                doc.build(elements)
                pdf_buffer.seek(0)
                return pdf_buffer

            if st.button("Generate PDF Report"):
                pdf_data = create_pdf(df)
                st.download_button(
                    label="Download PDF",
                    data=pdf_data,
                    file_name="benchmark_report.pdf",
                    mime="application/pdf"
                )

        # Human Review Tab
        with tab4:
             st.subheader("Human-in-the-loop Review")
             
             # Initialize SQLite
             import sqlite3
             conn = sqlite3.connect('human_feedback.db')
             c = conn.cursor()
             c.execute('''CREATE TABLE IF NOT EXISTS feedback
                          (model TEXT, prompt TEXT, response TEXT, rating INTEGER)''')
             conn.commit()
             
             st.write("Review model responses and provide feedback to improve future evaluations.")
             
             for index, row in df.iterrows():
                 with st.expander(f"{row['model']} - {row['prompt'][:30]}..."):
                     st.write(f"**Prompt:** {row['prompt']}")
                     st.write(f"**Response:** {row['response']}")
                     
                     col_a, col_b = st.columns(2)
                     if col_a.button("👍 Good", key=f"good_{index}"):
                         c.execute("INSERT INTO feedback VALUES (?, ?, ?, ?)", 
                                   (row['model'], row['prompt'], row['response'], 1))
                         conn.commit()
                         st.success("Saved Positive Feedback!")
                         
                     if col_b.button("👎 Bad", key=f"bad_{index}"):
                         c.execute("INSERT INTO feedback VALUES (?, ?, ?, ?)", 
                                   (row['model'], row['prompt'], row['response'], 0))
                         conn.commit()
                         st.error("Saved Negative Feedback!")
             
             # Show stats
             st.divider()
             st.subheader("Feedback Stats")
             feedback_df = pd.read_sql_query("SELECT * FROM feedback", conn)
             if not feedback_df.empty:
                 st.dataframe(feedback_df)
             else:
                 st.info("No feedback collected yet.")
             conn.close()

        # Quality Scores (if available)
        if 'quality_score' in df.columns: # Placeholder column check
            st.header("Quality Evaluation")
            st.bar_chart(df.set_index('model')['quality_score'])
            
st.sidebar.info("Run `python main.py` to generate new results.")
