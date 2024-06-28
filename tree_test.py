# Run these commands in Django shell
# python manage.py shell

from mlm_users.models import User

# Create root user (you)
root_user = User.objects.create_user(username='root', email='root@example.com', password='rootpassword')

# Create level 1 users
user1 = User.objects.create_user(username='user1', email='user1@example.com', password='user1password', sponsor=root_user)
user2 = User.objects.create_user(username='user2', email='user2@example.com', password='user2password', sponsor=root_user)

# Create level 2 users
user1_1 = User.objects.create_user(username='user1_1', email='user1_1@example.com', password='user1_1password', sponsor=user1)
user1_2 = User.objects.create_user(username='user1_2', email='user1_2@example.com', password='user1_2password', sponsor=user1)
user2_1 = User.objects.create_user(username='user2_1', email='user2_1@example.com', password='user2_1password', sponsor=user2)

# Create level 3 users
user1_1_1 = User.objects.create_user(username='user1_1_1', email='user1_1_1@example.com', password='user1_1_1password', sponsor=user1_1)
user1_2_1 = User.objects.create_user(username='user1_2_1', email='user1_2_1@example.com', password='user1_2_1password', sponsor=user1_2)

# Create level 4 users
user1_1_1_1 = User.objects.create_user(username='user1_1_1_1', email='user1_1_1_1@example.com', password='user1_1_1_1password', sponsor=user1_1_1)

# Create level 5 users
user1_1_1_1_1 = User.objects.create_user(username='user1_1_1_1_1', email='user1_1_1_1_1@example.com', password='user1_1_1_1_1password', sponsor=user1_1_1_1)

def display_team(user, level=0, max_depth=2):
    print('  ' * level + f"- {user.username}")
    if level < max_depth:
        for sponsored_user in user.sponsored_users.all():
            display_team(sponsored_user, level + 1, max_depth)

def check_team(user, max_depth=2):
    print(f"\nTeam structure for {user.username} (max depth: {max_depth}):")
    display_team(user, max_depth=max_depth)
    
    team = user.get_team(levels=max_depth)
    print(f"\nTeam members for {user.username}:")
    for member in team:
        print(f"Username: {member.username}, Sponsor: {member.sponsor.username if member.sponsor else 'None'}")
    
    print(f"\nTotal team members (excluding {user.username}): {len(team)}")

# Check team structure from different perspectives
check_team(root_user)  # Should show up to level 2
check_team(user1)      # Should show up to level 3
check_team(user1_1)    # Should show up to level 4
check_team(user1_1_1)  # Should show up to level 5

# Check if the view is limited to 2 levels for all users
print("\nChecking if view is limited to 2 levels for all users:")
for user in [root_user, user1, user1_1, user1_1_1]:
    team = user.get_team(levels=2)
    max_level = max(member.sponsor.level for member in team if member.sponsor) if team else 0
    print(f"{user.username}'s team max level: {max_level}")

# Verify that level 3+ users are not in root's team
root_team = root_user.get_team(levels=2)
level_3_plus_in_root_team = any(member.username in ['user1_1_1', 'user1_2_1', 'user1_1_1_1', 'user1_1_1_1_1'] for member in root_team)
print(f"\nLevel 3+ users in root's team: {level_3_plus_in_root_team}")

# Verify that level 5 user is in user1_1_1's team
user1_1_1_team = user1_1_1.get_team(levels=2)
level_5_in_user1_1_1_team = any(member.username == 'user1_1_1_1_1' for member in user1_1_1_team)
print(f"\nLevel 5 user in user1_1_1's team: {level_5_in_user1_1_1_team}")