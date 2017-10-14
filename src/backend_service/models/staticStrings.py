import random


class StaticStrings:

    # Asking for person type
    welcome = [
        "Hello {name}! To start off, are you a landlord or a tenant?",
        "Hey {name}, I'm here to help you with your rental disputes! Are you a landlord or a tenant?",
        "Nice to meet you {name}, are you a landlord or a tenant?",
        "You've got questions, I've got answers! Are you a landlord or a tenant, {name}?"
    ]

    # Asking for initial problem description
    problem_inquiry = [
        "So {name}, I see you're a {person_type}. What issue can I help you with today?",
        "What kind of issue are you having as a {person_type}, {name}?",
        "I can help you with all sorts of {person_type} issues, {name}! Describe your problem to me, let's see what we can do."
    ]

    # Acknowledge claim category resolution
    category_acknowledge = [
        "I see, you're having issues with {claim_category}. {first_question}",
        "As I understand it, your problems have to do with {claim_category}. {first_question}",
        "Oh yes, I know all about problems with {claim_category}. {first_question}"
    ]

    # Asking for clarification
    clarify = [
        "I'm sorry, I can't understand what you mean.",
        "I didn't understand that, could you please clarify?",
        "Huh?"
    ]

    @staticmethod
    def chooseFrom(strings):
        choice = random.choice
        return choice(strings)