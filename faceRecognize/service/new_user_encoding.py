from copy import deepcopy

from django.contrib.auth.models import User
from django.db import transaction
from imutils import paths
import pickle
import cv2
import os
import face_recognition

from user.models import SmartLockUser


def load_existing_encodings(encoding_path):
    if os.path.exists(encoding_path) and os.path.getsize(encoding_path) > 0:
        with open(encoding_path, "rb") as f:
            data = pickle.load(f)
        known_encodings = data["encodings"]
        known_names = data["names"]

    else:
        known_encodings = []
        known_names = []

    return known_encodings, known_names


def save_encodings(encoding_path, data):
    with open(encoding_path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def process_user_images(user_path, detection_method, user_id):
    encodings = []
    names = []

    image_paths = list(paths.list_images(user_path))
    for (i, image_path) in enumerate(image_paths):
        print("[INFO] Processing image {}/{}".format(i + 1, len(image_paths)))
        name = user_id

        image = cv2.imread(image_path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model=detection_method)
        user_encodings = face_recognition.face_encodings(rgb, boxes)

        encodings.extend(user_encodings)
        names.extend([name] * len(user_encodings))

    return encodings, names

@transaction.atomic
def encode_faces(dataset_dir, detection_method, encoding_path):
    try:
        print("[INFO] Quantifying faces...")
        known_encodings, known_names = load_existing_encodings(encoding_path)
        users = SmartLockUser.objects.all().in_bulk(field_name='pk')
        encoding_users = []
        encoded_users = []
        for user_dir in os.listdir(dataset_dir):
            user_path = os.path.join(dataset_dir, user_dir)
            if not os.path.isdir(user_path):
                continue

            user_id = user_dir

            if user_id in known_names or int(user_id) not in users.keys():
                continue
            encoding_users.append(user_id)
            encodings, names = process_user_images(user_path, detection_method, user_id)

            known_encodings.extend(encodings)
            known_names.extend(names)

        data = {"encodings": known_encodings, "names": known_names}
        save_encodings(encoding_path, data)

        for id in encoding_users:
            if user := users.get(int(id)):
                user.encode = True
                encoded_users.append(user)

        SmartLockUser.objects.bulk_update(encoded_users, ["encode"])

        return encoded_users
    except FileNotFoundError as e:
        print("File not found while encoding:", str(e))
        raise e
    except ValueError as e:
        print("Value error occurred while encoding:", str(e))
        raise e
    except Exception as e:
        print("An error occurred during encoding:", str(e))
        raise e


@transaction.atomic
def encode_faces_for_id(dataset_dir, detection_method, encoding_path, user_id):
    try:
        user_id = str(user_id)
        known_encodings, known_names = load_existing_encodings(encoding_path)

        if user_id not in known_names:
            user_path = os.path.join(dataset_dir, user_id)
            if not os.path.isdir(user_path):
                raise FileNotFoundError(f"User directory with ID {user_id} not found in dataset.")

            encodings, names = process_user_images(user_path, detection_method, user_id)

            known_encodings.extend(encodings)
            known_names.extend(names)

            data = {"encodings": known_encodings, "names": known_names}
            save_encodings(encoding_path, data)

            try:
                user = SmartLockUser.objects.filter(user_ptr_id=int(user_id)).first()
                user.encode = True
                user.save()
                return user
            except SmartLockUser.DoesNotExist:
                print(f"SmartLockUser with ID {user_id} not found.")
                return None
        return None
    except FileNotFoundError as e:
        print("File not found while encoding for user ID", user_id, ":", str(e))
        raise e
    except ValueError as e:
        print("Value error occurred while encoding for user ID", user_id, ":", str(e))
        raise e
    except Exception as e:
        print("An error occurred during encoding for user ID", user_id, ":", str(e))
        raise e


@transaction.atomic
def delete_encoding_for_id(encoding_path, user):
    try:
        user_id = str(user.id)
        known_encodings, known_names = load_existing_encodings(encoding_path)

        if user_id in known_names:
            while user_id in known_names:
                user_index = known_names.index(user_id)
                known_encodings.pop(user_index)
                known_names.pop(user_index)

            data = {"encodings": known_encodings, "names": known_names}
            save_encodings(encoding_path, data)

            try:
                user.encode = False
                user.save()
            except SmartLockUser.DoesNotExist:
                print(f"SmartLockUser with ID {user_id} not found.")
                return False
            return True
        else:
            print(f"User with ID {user_id} not found in encoding data.")
            return False
    except FileNotFoundError as e:
        print("File not found while deleting encoding for user ID", user_id, ":", str(e))
        raise e
    except ValueError as e:
        print("Value error occurred while deleting encoding for user ID", user_id, ":", str(e))
        raise e
    except Exception as e:
        print("An error occurred during deleting encoding for user ID", user_id, ":", str(e))
        raise e
