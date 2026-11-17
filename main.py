
def main():
    print("\n===== Welcome to MockMate =====")
    print("Your AI Mock Interview Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("MockMate: Thank you for using MockMate!")
            break

        print("MockMate:", user_input)


if __name__ == "__main__":
    main()
