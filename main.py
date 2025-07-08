from crewai import Agent,Task,Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from modules.notebook_tools_crewai import NOTEBOOK_TOOLS

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key="AIzaSyD9wRJTtU5A7uyoGR1JT5B3pe8w0HMtl9g")

agent = Agent(
    role="Data Analyst and Scientist",
    goal="Treating Missing value, feature selection, feature deduction",
    max_iter=50,
    backstory="\n".join([
        "Make sure u dont use any comments while inserting the code and also use markdown if needed",
        "You will be given access to the Notebook tools, and your job will be to use these tool",
        "to Analyse and access the given dataset using popular libraries like pandas, matplotlib, numpy and scikit learn.",
        "Then you have perform various techniques like feature engineering, feature selection, EDA and deduction.",
        "The Goal is prepare dataset for final model training and then at the end do some visualisation for user to understand the",
        "Final cleaned data. Also Suggest few best models at the end.",
        "Allowed Libraries are : Scikit-learn, Seaborn, matplotlib, numpy, pandas, tabulate, There are already installed."
    ]),
    verbose=True,
    tools=NOTEBOOK_TOOLS
)

def run_crew_with_user_input():
    print("🚀 EDA Agent is ready.")
    while True:
        user_input = input("\n📝 Describe your data analysis task (or type 'exit'): ")
        if user_input.lower() in ['exit', 'quit']:
            print("👋 Exiting the EDA Agent.")
            break

        task = Task(
            name="Custom EDA Task",
            agent=agent,
            description=user_input,
            expected_output="Final cleaned CSV dataset saved and visualizations created."
        )

        crew = Crew(
            name="Custom EDA Crew",
            agents=[agent],
            tasks=[task]
        )

        print("\n🔄 Running the agent...")
        result = crew.kickoff()
        print("\n✅ Task Complete:\n", result)

run_crew_with_user_input()