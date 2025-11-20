def generate_profile(age):
    if current_age <= 12:
        return 'Child'
    elif current_age <= 19:
        return 'Teenager'
    elif current_age >= 20:
        return 'Adult'

user_name = input('Enter your full name: ')

birth_year_str = input('Enter your birth year: ')
birth_year = int(birth_year_str)
current_age = 2025 - birth_year
life_stage = generate_profile(current_age)

hobbies = []
while True:
    hobby = input("Enter a favorite hobby or type 'stop' to finish: ")
    if hobby == 'stop':
        break
    hobbies.append(hobby)


user_profile = {
    'name': user_name,
    'age': current_age,
    'stage': life_stage,
    'hobbies': hobbies
}

print('Profile Summary:')
print(f"Name: {user_profile['name']}")
print(f"Age: {user_profile['age']}")
print(f"Life Stage: {user_profile['stage']}")

if hobbies == []:
    print("You didn't mention any hobbies")
else:
    print(f"Favorite Hobbies ({len(user_profile['hobbies'])}):")
    for i in user_profile['hobbies']:
        print(f"- {i}")