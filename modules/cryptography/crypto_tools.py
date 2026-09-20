# ============================================================
# NIGHT HUNTER - Cryptography Tools
# ============================================================
# General-purpose cryptographic and encoding utilities.
#
# Features:
# - MD5
# - SHA-1
# - SHA-224
# - SHA-256
# - SHA-384
# - SHA-512
# - SHA3-224
# - SHA3-256
# - SHA3-384
# - SHA3-512
# - BLAKE2b
# - BLAKE2s
# - Base64 encoding / decoding
# - Hex encoding / decoding
# - URL encoding / decoding
# - ROT13
# - Caesar Cipher
# - XOR utility
# - Text hash generation
# - File hash generation
# - Hash verification
#
# ============================================================

import base64
import hashlib
import urllib.parse
from pathlib import Path


# ============================================================
# SUPPORTED HASH ALGORITHMS
# ============================================================

HASH_ALGORITHMS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
    "sha3_224": hashlib.sha3_224,
    "sha3_256": hashlib.sha3_256,
    "sha3_384": hashlib.sha3_384,
    "sha3_512": hashlib.sha3_512,
    "blake2b": hashlib.blake2b,
    "blake2s": hashlib.blake2s,
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def normalize_algorithm(algorithm):
    """
    Normalize a hash algorithm name.

    Examples:
        SHA-256   -> sha256
        SHA256    -> sha256
        sha_256   -> sha256
    """

    if not algorithm:
        return ""

    value = str(algorithm).strip().lower()

    replacements = {
        "-": "",
        "_": "",
        " ": "",
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    aliases = {
        "md5": "md5",
        "sha1": "sha1",
        "sha224": "sha224",
        "sha256": "sha256",
        "sha384": "sha384",
        "sha512": "sha512",
        "sha3224": "sha3_224",
        "sha3256": "sha3_256",
        "sha3384": "sha3_384",
        "sha3512": "sha3_512",
        "blake2b": "blake2b",
        "blake2s": "blake2s",
    }

    return aliases.get(value, value)


def get_supported_algorithms():
    """Return a list of supported hashing algorithms."""

    return list(HASH_ALGORITHMS.keys())


# ============================================================
# TEXT HASHING
# ============================================================

def hash_text(text, algorithm="sha256"):
    """
    Generate a cryptographic hash from text.

    Returns:
        Hexadecimal digest string.
    """

    if text is None:
        raise ValueError("Text cannot be None.")

    algorithm = normalize_algorithm(algorithm)

    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(
            f"Unsupported hash algorithm: {algorithm}"
        )

    data = str(text).encode("utf-8")

    hasher = HASH_ALGORITHMS[algorithm]()

    hasher.update(data)

    return hasher.hexdigest()


# ============================================================
# TEXT HASH ALL
# ============================================================

def hash_text_all(text):
    """
    Generate all supported hashes for a piece of text.

    Returns:
        Dictionary containing algorithm -> digest.
    """

    results = {}

    for algorithm in HASH_ALGORITHMS:
        try:
            results[algorithm] = hash_text(
                text,
                algorithm
            )
        except Exception as error:
            results[algorithm] = f"ERROR: {error}"

    return results


# ============================================================
# FILE HASHING
# ============================================================

def hash_file(
    file_path,
    algorithm="sha256",
    chunk_size=1024 * 1024
):
    """
    Generate a hash for a file.

    The file is processed in chunks so large files do not
    need to be loaded completely into memory.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    algorithm = normalize_algorithm(algorithm)

    if algorithm not in HASH_ALGORITHMS:
        raise ValueError(
            f"Unsupported hash algorithm: {algorithm}"
        )

    hasher = HASH_ALGORITHMS[algorithm]()

    with path.open("rb") as file:

        while True:

            chunk = file.read(chunk_size)

            if not chunk:
                break

            hasher.update(chunk)

    return hasher.hexdigest()


# ============================================================
# FILE HASH ALL
# ============================================================

def hash_file_all(file_path):
    """
    Generate all supported hashes for a file.
    """

    results = {}

    for algorithm in HASH_ALGORITHMS:

        try:

            results[algorithm] = hash_file(
                file_path,
                algorithm
            )

        except Exception as error:

            results[algorithm] = (
                f"ERROR: {error}"
            )

    return results


# ============================================================
# HASH VERIFICATION
# ============================================================

def verify_hash(
    text,
    expected_hash,
    algorithm="sha256"
):
    """
    Verify whether a text value produces the expected hash.
    """

    if expected_hash is None:
        return False

    calculated = hash_text(
        text,
        algorithm
    )

    return calculated.lower() == str(
        expected_hash
    ).strip().lower()


def verify_file_hash(
    file_path,
    expected_hash,
    algorithm="sha256"
):
    """
    Verify whether a file matches an expected hash.
    """

    if expected_hash is None:
        return False

    calculated = hash_file(
        file_path,
        algorithm
    )

    return calculated.lower() == str(
        expected_hash
    ).strip().lower()


# ============================================================
# BASE64
# ============================================================

def base64_encode(text):
    """
    Encode text using Base64.
    """

    if text is None:
        raise ValueError("Text cannot be None.")

    data = str(text).encode("utf-8")

    encoded = base64.b64encode(data)

    return encoded.decode("ascii")


def base64_decode(encoded_text):
    """
    Decode Base64 text.

    Raises:
        ValueError when the input is invalid Base64.
    """

    if encoded_text is None:
        raise ValueError(
            "Encoded text cannot be None."
        )

    try:

        decoded = base64.b64decode(
            str(encoded_text),
            validate=True
        )

        return decoded.decode(
            "utf-8",
            errors="replace"
        )

    except Exception as error:

        raise ValueError(
            f"Invalid Base64 data: {error}"
        )


# ============================================================
# HEX
# ============================================================

def hex_encode(text):
    """
    Convert text to hexadecimal representation.
    """

    if text is None:
        raise ValueError("Text cannot be None.")

    return str(text).encode(
        "utf-8"
    ).hex()


def hex_decode(hex_text):
    """
    Convert hexadecimal data back to text.
    """

    if hex_text is None:
        raise ValueError(
            "Hex text cannot be None."
        )

    value = str(hex_text).strip()

    if len(value) % 2 != 0:
        raise ValueError(
            "Hex data must contain an even number of characters."
        )

    try:

        decoded = bytes.fromhex(value)

        return decoded.decode(
            "utf-8",
            errors="replace"
        )

    except ValueError as error:

        raise ValueError(
            f"Invalid hexadecimal data: {error}"
        )


# ============================================================
# URL ENCODING
# ============================================================

def url_encode(text):
    """
    URL-encode text.
    """

    if text is None:
        raise ValueError("Text cannot be None.")

    return urllib.parse.quote(
        str(text),
        safe=""
    )


def url_decode(encoded_text):
    """
    Decode URL-encoded text.
    """

    if encoded_text is None:
        raise ValueError(
            "Encoded text cannot be None."
        )

    return urllib.parse.unquote(
        str(encoded_text)
    )


# ============================================================
# ROT13
# ============================================================

def rot13(text):
    """
    Apply ROT13 transformation.

    ROT13 is an encoding/obfuscation method,
    not a secure encryption algorithm.
    """

    if text is None:
        raise ValueError("Text cannot be None.")

    result = []

    for character in str(text):

        if "a" <= character <= "z":

            result.append(
                chr(
                    (ord(character) - ord("a") + 13)
                    % 26
                    + ord("a")
                )
            )

        elif "A" <= character <= "Z":

            result.append(
                chr(
                    (ord(character) - ord("A") + 13)
                    % 26
                    + ord("A")
                )
            )

        else:

            result.append(character)

    return "".join(result)


# ============================================================
# CAESAR CIPHER
# ============================================================

def caesar_encrypt(text, shift=3):
    """
    Encrypt text using a Caesar cipher.
    """

    if text is None:
        raise ValueError("Text cannot be None.")

    try:
        shift = int(shift)
    except (TypeError, ValueError):
        raise ValueError(
            "Shift must be an integer."
        )

    result = []

    for character in str(text):

        if "a" <= character <= "z":

            result.append(
                chr(
                    (
                        ord(character)
                        - ord("a")
                        + shift
                    ) % 26
                    + ord("a")
                )
            )

        elif "A" <= character <= "Z":

            result.append(
                chr(
                    (
                        ord(character)
                        - ord("A")
                        + shift
                    ) % 26
                    + ord("A")
                )
            )

        else:

            result.append(character)

    return "".join(result)


def caesar_decrypt(text, shift=3):
    """
    Decrypt text encrypted with a Caesar cipher.
    """

    return caesar_encrypt(
        text,
        -int(shift)
    )


# ============================================================
# XOR
# ============================================================

def xor_bytes(data, key):
    """
    XOR byte data with a repeating key.

    This is a demonstration/utility operation.
    XOR alone is NOT secure encryption.
    """

    if not data:
        raise ValueError(
            "Data cannot be empty."
        )

    if not key:
        raise ValueError(
            "Key cannot be empty."
        )

    if isinstance(data, str):
        data = data.encode("utf-8")

    if isinstance(key, str):
        key = key.encode("utf-8")

    result = bytearray()

    for index, value in enumerate(data):

        result.append(
            value ^ key[index % len(key)]
        )

    return bytes(result)


def xor_encode(text, key):
    """
    XOR text and return hexadecimal output.
    """

    result = xor_bytes(
        text,
        key
    )

    return result.hex()


def xor_decode(hex_text, key):
    """
    Decode hexadecimal XOR data back to text.
    """

    if not hex_text:
        raise ValueError(
            "XOR data cannot be empty."
        )

    try:

        data = bytes.fromhex(
            str(hex_text)
        )

    except ValueError as error:

        raise ValueError(
            f"Invalid XOR hexadecimal data: {error}"
        )

    result = xor_bytes(
        data,
        key
    )

    return result.decode(
        "utf-8",
        errors="replace"
    )


# ============================================================
# HASH IDENTIFICATION
# ============================================================

def identify_common_hash(hash_value):
    """
    Estimate common hash types from digest length.

    This is only a basic length-based identification.
    Different algorithms can produce strings of the same
    length, so this function does not guarantee the algorithm.
    """

    if not hash_value:
        return []

    value = str(hash_value).strip()

    candidates = []

    if len(value) == 32:
        candidates.append("MD5")

    if len(value) == 40:
        candidates.append("SHA-1")

    if len(value) == 56:
        candidates.append("SHA-224")

    if len(value) == 64:
        candidates.extend([
            "SHA-256",
            "SHA3-256",
            "BLAKE2s-256"
        ])

    if len(value) == 96:
        candidates.extend([
            "SHA-384",
            "SHA3-384"
        ])

    if len(value) == 128:
        candidates.extend([
            "SHA-512",
            "SHA3-512",
            "BLAKE2b-512"
        ])

    return candidates


# ============================================================
# HASH INFORMATION
# ============================================================

def get_hash_information(hash_value):
    """
    Return basic information about a hash string.
    """

    if hash_value is None:
        raise ValueError(
            "Hash value cannot be None."
        )

    value = str(hash_value).strip()

    hexadecimal = all(
        character in "0123456789abcdefABCDEF"
        for character in value
    )

    return {
        "value": value,
        "length": len(value),
        "hexadecimal": hexadecimal,
        "possible_algorithms":
            identify_common_hash(value)
    }


# ============================================================
# FILE INTEGRITY COMPARISON
# ============================================================

def compare_file_hashes(
    file_path_1,
    file_path_2,
    algorithm="sha256"
):
    """
    Compare the cryptographic hashes of two files.
    """

    hash_1 = hash_file(
        file_path_1,
        algorithm
    )

    hash_2 = hash_file(
        file_path_2,
        algorithm
    )

    return {
        "file_1": str(file_path_1),
        "file_2": str(file_path_2),
        "algorithm": normalize_algorithm(
            algorithm
        ),
        "hash_1": hash_1,
        "hash_2": hash_2,
        "identical": hash_1 == hash_2
    }


# ============================================================
# TEXT INTEGRITY
# ============================================================

def compare_text_hashes(
    text_1,
    text_2,
    algorithm="sha256"
):
    """
    Compare two text values using cryptographic hashes.
    """

    hash_1 = hash_text(
        text_1,
        algorithm
    )

    hash_2 = hash_text(
        text_2,
        algorithm
    )

    return {
        "algorithm": normalize_algorithm(
            algorithm
        ),
        "hash_1": hash_1,
        "hash_2": hash_2,
        "identical": hash_1 == hash_2
    }


# ============================================================
# INFORMATION DISPLAY
# ============================================================

def display_hashes(results):
    """
    Display a dictionary of hashes.
    """

    print()
    print("=" * 65)
    print("HASH RESULTS")
    print("=" * 65)

    for algorithm, digest in results.items():

        print(
            f"{algorithm:<15}: {digest}"
        )

    print("=" * 65)


def display_hash_information(info):
    """
    Display information about a hash.
    """

    print()
    print("=" * 65)
    print("HASH INFORMATION")
    print("=" * 65)

    print(
        f"Value       : {info.get('value')}"
    )

    print(
        f"Length      : {info.get('length')}"
    )

    print(
        f"Hexadecimal : {info.get('hexadecimal')}"
    )

    candidates = info.get(
        "possible_algorithms",
        []
    )

    if candidates:

        print(
            "Possible    : "
            + ", ".join(candidates)
        )

    else:

        print(
            "Possible    : No common match"
        )

    print("=" * 65)


# ============================================================
# INTERACTIVE TOOL
# ============================================================

def interactive_mode():

    while True:

        print()
        print("=" * 65)
        print("NIGHT HUNTER - CRYPTOGRAPHY TOOLS")
        print("=" * 65)

        print("[1] Hash Text")
        print("[2] Hash Text With All Algorithms")
        print("[3] Verify Text Hash")
        print("[4] Base64 Encode")
        print("[5] Base64 Decode")
        print("[6] Hex Encode")
        print("[7] Hex Decode")
        print("[8] URL Encode")
        print("[9] URL Decode")
        print("[10] ROT13")
        print("[11] Caesar Cipher")
        print("[12] XOR Utility")
        print("[13] Identify Hash")
        print("[14] Hash File")
        print("[15] Hash File With All Algorithms")
        print("[16] Verify File Hash")
        print("[0] Exit")

        choice = input(
            "\nSelect option: "
        ).strip()

        # ----------------------------------------------------
        # HASH TEXT
        # ----------------------------------------------------

        if choice == "1":

            text = input(
                "\nEnter text: "
            )

            algorithm = input(
                "Enter algorithm [sha256]: "
            ).strip()

            if not algorithm:
                algorithm = "sha256"

            try:

                result = hash_text(
                    text,
                    algorithm
                )

                print()
                print(
                    f"{algorithm.upper()}: {result}"
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # HASH TEXT ALL
        # ----------------------------------------------------

        elif choice == "2":

            text = input(
                "\nEnter text: "
            )

            try:

                results = hash_text_all(
                    text
                )

                display_hashes(results)

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # VERIFY TEXT HASH
        # ----------------------------------------------------

        elif choice == "3":

            text = input(
                "\nEnter text: "
            )

            expected = input(
                "Enter expected hash: "
            ).strip()

            algorithm = input(
                "Enter algorithm [sha256]: "
            ).strip()

            if not algorithm:
                algorithm = "sha256"

            try:

                valid = verify_hash(
                    text,
                    expected,
                    algorithm
                )

                if valid:
                    print(
                        "\n[+] Hash matches."
                    )
                else:
                    print(
                        "\n[-] Hash does not match."
                    )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # BASE64 ENCODE
        # ----------------------------------------------------

        elif choice == "4":

            text = input(
                "\nEnter text: "
            )

            try:

                print(
                    "\nEncoded:",
                    base64_encode(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # BASE64 DECODE
        # ----------------------------------------------------

        elif choice == "5":

            text = input(
                "\nEnter Base64: "
            )

            try:

                print(
                    "\nDecoded:",
                    base64_decode(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # HEX ENCODE
        # ----------------------------------------------------

        elif choice == "6":

            text = input(
                "\nEnter text: "
            )

            try:

                print(
                    "\nHex:",
                    hex_encode(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # HEX DECODE
        # ----------------------------------------------------

        elif choice == "7":

            text = input(
                "\nEnter hexadecimal: "
            )

            try:

                print(
                    "\nDecoded:",
                    hex_decode(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # URL ENCODE
        # ----------------------------------------------------

        elif choice == "8":

            text = input(
                "\nEnter text: "
            )

            try:

                print(
                    "\nEncoded:",
                    url_encode(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # URL DECODE
        # ----------------------------------------------------

        elif choice == "9":

            text = input(
                "\nEnter URL-encoded text: "
            )

            try:

                print(
                    "\nDecoded:",
                    url_decode(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # ROT13
        # ----------------------------------------------------

        elif choice == "10":

            text = input(
                "\nEnter text: "
            )

            try:

                print(
                    "\nResult:",
                    rot13(text)
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # CAESAR
        # ----------------------------------------------------

        elif choice == "11":

            text = input(
                "\nEnter text: "
            )

            shift = input(
                "Enter shift [3]: "
            ).strip()

            if not shift:
                shift = "3"

            try:

                shift = int(shift)

                encrypted = caesar_encrypt(
                    text,
                    shift
                )

                decrypted = caesar_decrypt(
                    encrypted,
                    shift
                )

                print(
                    "\nEncrypted:",
                    encrypted
                )

                print(
                    "Decrypted:",
                    decrypted
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # XOR
        # ----------------------------------------------------

        elif choice == "12":

            text = input(
                "\nEnter text: "
            )

            key = input(
                "Enter XOR key: "
            )

            try:

                encoded = xor_encode(
                    text,
                    key
                )

                decoded = xor_decode(
                    encoded,
                    key
                )

                print(
                    "\nEncoded:",
                    encoded
                )

                print(
                    "Decoded:",
                    decoded
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # IDENTIFY HASH
        # ----------------------------------------------------

        elif choice == "13":

            value = input(
                "\nEnter hash: "
            ).strip()

            try:

                info = get_hash_information(
                    value
                )

                display_hash_information(
                    info
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # HASH FILE
        # ----------------------------------------------------

        elif choice == "14":

            file_path = input(
                "\nEnter file path: "
            ).strip()

            algorithm = input(
                "Enter algorithm [sha256]: "
            ).strip()

            if not algorithm:
                algorithm = "sha256"

            try:

                digest = hash_file(
                    file_path,
                    algorithm
                )

                print()
                print(
                    f"{algorithm.upper()}: {digest}"
                )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # HASH FILE ALL
        # ----------------------------------------------------

        elif choice == "15":

            file_path = input(
                "\nEnter file path: "
            ).strip()

            try:

                results = hash_file_all(
                    file_path
                )

                display_hashes(results)

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # VERIFY FILE
        # ----------------------------------------------------

        elif choice == "16":

            file_path = input(
                "\nEnter file path: "
            ).strip()

            expected = input(
                "Enter expected hash: "
            ).strip()

            algorithm = input(
                "Enter algorithm [sha256]: "
            ).strip()

            if not algorithm:
                algorithm = "sha256"

            try:

                valid = verify_file_hash(
                    file_path,
                    expected,
                    algorithm
                )

                if valid:

                    print(
                        "\n[+] File hash matches."
                    )

                else:

                    print(
                        "\n[-] File hash does not match."
                    )

            except Exception as error:

                print(
                    f"\n[!] Error: {error}"
                )

        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        elif choice == "0":

            print(
                "\n[*] Exiting Cryptography Tools..."
            )

            break

        # ----------------------------------------------------
        # INVALID
        # ----------------------------------------------------

        else:

            print(
                "\n[!] Invalid option."
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("                 NIGHT HUNTER")
    print("                CRYPTOGRAPHY")
    print("=" * 65)

    print(
        "General-purpose cryptographic utilities"
    )

    interactive_mode()