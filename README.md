# 💸 ExpenseIQ

**ExpenseIQ** is an interactive financial management application designed to help users track spending, parse bank statements, and visualize expenses. Built with **Streamlit**, **SQLite**, and **Plotly**, the app automates transaction parsing and categorizes spending to make personal finance management intuitive and effortless.

🚀 **[Live Demo](https://expenseiq-prototype.streamlit.app/)**

---

## ✨ Features Currently Built

- **🔐 Secure User Authentication:** Full sign-up and login workflows connected to a local SQLite database with multi-screen session management.
- **📄 Bank Statement Parsing:** Extracts spending data and monetary amounts from uploaded PDF bank statements using `PyPDF` and regular expressions (`regex`).
- **🎡 Interactive Spending Wheel:** Renders dynamic donut charts via **Plotly Express** to visually break down spending by category (*Groceries, Utilities, Dining, Shopping, ATM Withdrawals, etc.*).
- **📋 Categorized Transaction Breakdown:** Displays parsed item descriptions, categories, and amounts in filterable interactive tables.
- **📂 Statement History Management:** Stores metadata and file records locally with options to search, filter, and delete records safely using popover confirmations.
- **⚡ 24/7 Cloud Uptime:** Integrated **GitHub Actions** CI/CD workflow to keep the Streamlit Cloud instance active without sleeping.

---

## 🔮 Planned Enhancements

- [ ] Multi-month spending trend analysis across multiple uploaded statements
- [ ] AI-assisted expense classification for edge-case statement descriptions
- [ ] Customizable monthly budget limits and overspending alerts
- [ ] PDF export for generated financial summaries

---

## 🛠️ Tech Stack

- **Frontend & App Framework:** Streamlit
- **Backend & Storage:** Python, SQLite
- **Data Processing & Analytics:** Pandas, PyPDF, Regex
- **Data Visualization:** Plotly Express
- **DevOps & Automation:** Git, GitHub Actions, Streamlit Cloud

---

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/pkyeibrewu1/ExpenselQ.git](https://github.com/yourusername/ExpenseIQ.git)
   cd ExpenseIQ