from research_agent import generate_answer


def get_user_question():
    """Take a research question from the user."""
    return input("Enter your research question: ").strip()


def process_question(question):
    """Validate the user's question."""
    if not question:
        return None

    return question


def main():
    """Run the research agent."""

    # Step 1: Get question
    question = get_user_question()

    # Step 2: Validate question
    question = process_question(question)

    if question is None:
        print("Please enter a valid question.")
        return

    # Step 3: Generate research report
    answer = generate_answer(question)

    # Step 4: Display report
    print(f"\nAI Research Report:\n{answer}")


if __name__ == "__main__":
    main()