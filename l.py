from werkzeug.security import generate_password_hash, check_password_hash

password = "qwerty"


def hashed_password(password):
    password_hash = generate_password_hash(password)
    print(password_hash)


hashed_password(password)


def check_password(password):
    return check_password_hash(
        "pbkdf2:sha256:260000$oCA9NTShZrjzmpew$224e4fb3a91539fcb94e529e6b4a809066f1f92f652a7fd67af2e4827581556b",
        password,
    )
    # print(password_checker)


print(check_password(password))

print(len("scrypt:32768:8:1$IbXuXcLQ1laRNNqP$84c41e1612de48ffc016d4735fd8d02818e6fba2db9b09ae2896c7cb49a4258670d1204b34e212aecacab5cf52dba4e349fd0a44361f15ad837b7d69c2f92706"))
