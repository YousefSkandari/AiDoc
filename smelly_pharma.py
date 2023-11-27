import os
import openai
import json
import re

# Initialize the OpenAI API with your API key
openai.api_key = "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"

def get_model_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=3800,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def get_confidence_score(prompt):
    prompt += " Based on the information provided so far, what is your confidence score in your diagnosis and recommendations, out of 100?"
    response = get_model_response(prompt)
    match = re.search(r'\b\d+\b', response)
    if match:
        return int(match.group())
    else:
        return 0

def get_treatment_rundown(prompt):
    prompt += " Please provide a detailed rundown on how to take the recommended treatment, potential side effects, and any precautions for certain groups of people."
    return get_model_response(prompt)

def get_medicine_recommendation(symptoms, additional_info=None):
    prompt = f"I am an AI trained to suggest potential diagnoses, medications, or treatments for various symptoms. The user has reported the following symptoms: {symptoms}."
    
    if additional_info:
        prompt += f" The user has provided the following additional information: {additional_info}. Please consider all the information and suggest an alternative diagnosis or solution if necessary."
    
    prompt += " What is your potential diagnosis and what potential medicine or treatment do you recommend?"

    response = get_model_response(prompt)
    confidence_score = get_confidence_score(prompt)
    
    return response, confidence_score

def main():
    print("Welcome to the Pharmacy Bot!")
    print("Enter your symptoms separated by commas (e.g., headache, cough, fever):")

    symptoms = input()
    recommendations, confidence_score = get_medicine_recommendation(symptoms)

    conversation_log = {
        "symptoms": symptoms,
        "recommendations": [(recommendations, confidence_score)],
        "additional_info": [],
        "treatment_rundown": "",
        "user_condition": "",
        "alternative_recommendations": []
    }

    print(f"\nBased on your symptoms, I recommend the following with a confidence score of {confidence_score}:")
    print(recommendations)

    while True:
        print("\nDo you want to provide more information? (y/n)")
        user_input = input().lower()

        if user_input == "y":
            print("Please provide additional information:")
            additional_info = input()
            conversation_log["additional_info"].append(additional_info)
            updated_recommendations, updated_confidence_score = get_medicine_recommendation(symptoms, ', '.join(conversation_log["additional_info"]))

            print(f"\nBased on the updated information and considering alternative solutions, I recommend the following with a confidence score of {updated_confidence_score}:")
            print(updated_recommendations)
            conversation_log["recommendations"].append((updated_recommendations, updated_confidence_score))
        else:
            break

    treatment_rundown = get_treatment_rundown(recommendations)
    conversation_log["treatment_rundown"] = treatment_rundown

    print("\nHere's a rundown on how to take the recommended treatment, potential side effects, and any precautions:")
    print(treatment_rundown)

    print("\nDoes the recommended treatment have potential fatal side effectsfor a particular group of people that affect you? (y/n)")
    user_input = input().lower()

    if user_input == "y":
        print("Please provide information about the condition or group that affects you:")
        user_condition = input()
        conversation_log["user_condition"] = user_condition
        alternative_recommendations, alt_confidence_score = get_medicine_recommendation(symptoms, f"{', '.join(conversation_log['additional_info'])}, {user_condition}")
        conversation_log["alternative_recommendations"].append((alternative_recommendations, alt_confidence_score))

        if alt_confidence_score < 100:
            print("\nConsidering your condition, I cannot provide a specific alternative treatment with full confidence.")
            print("It is important to consult a healthcare professional for an accurate medical assessment and appropriate treatment based on your personal conditions.")
        else:
            print(f"\nConsidering your condition, I recommend the following alternative treatment with a confidence score of {alt_confidence_score}:")
            print(alternative_recommendations)
    else:
        print("\nFollow the provided guidelines for the recommended treatment. If you have any concerns, please consult a healthcare professional for accurate medical advice.")
    
    while True:
        print("\nYou can now openly ask questions about your health. Type 'exit' to end the conversation.")
        user_question = input()

        if user_question.lower() == 'exit':
            break

        response = get_model_response(user_question)
        print(response)

if __name__ == "__main__":
    main()
