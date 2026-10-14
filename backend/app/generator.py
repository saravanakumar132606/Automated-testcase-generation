import os
import json
import logging
from typing import List, Dict, Any, Optional, Set
from .models import CodeAnalysis, TestCaseItem
from .oracle import ReferenceOracle

logger = logging.getLogger(__name__)

def format_inputs(inputs: Dict[str, Any]) -> str:
    """Formats a dictionary of inputs into standard human-readable format."""
    lines = []
    for k, v in inputs.items():
        if isinstance(v, str):
            lines.append(f'{k} = "{v}"')
        else:
            lines.append(f'{k} = {json.dumps(v)}')
    return "\n".join(lines)

def normalize_input_signature(inputs: Dict[str, Any]) -> str:
    """Produces a deterministic string for deduplication."""
    return json.dumps(inputs, sort_keys=True)


class TestCaseGenerator:
    """
    Generates meaningful, logic-based test cases for source code
    across 9 essential categories. Guarantees a minimum of 100 test cases.
    """

    @classmethod
    def _get_anagram_cases(cls) -> List[Dict[str, Any]]:
        cases = []

        # 1. Normal and Representative (20 cases)
        normal_pairs = [
            ("listen", "silent", "Standard anagram pair containing identical characters."),
            ("elbow", "below", "Standard 5-letter valid anagram."),
            ("evil", "vile", "Standard 4-letter valid anagram."),
            ("dusty", "study", "Common lowercase English word anagram."),
            ("night", "thing", "5-letter word anagram with mixed consonants."),
            ("stressed", "desserts", "Reversible anagram word pair."),
            ("cat", "act", "3-letter basic anagram."),
            ("cinema", "iceman", "6-letter valid anagram."),
            ("players", "parsley", "7-letter valid anagram."),
            ("heart", "earth", "5-letter valid anagram."),
            ("stop", "pots", "Common 4-letter anagram."),
            ("stone", "notes", "Common 5-letter anagram."),
            ("rescue", "secure", "6-letter valid anagram."),
            ("binary", "brainy", "6-letter word anagram."),
            ("friend", "finder", "Valid anagram with repeated letter 'r'."),
            ("cider", "cried", "Standard valid anagram."),
            ("alert", "alter", "Standard 5-letter anagram."),
            ("cloud", "could", "Standard 5-letter anagram."),
            ("table", "bleat", "Standard 5-letter anagram."),
            ("drawer", "reward", "6-letter valid anagram.")
        ]
        for s, t, r in normal_pairs:
            cases.append({
                "title": f"Valid Anagram: {s} vs {t}",
                "category": "Normal and Representative",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 2. Meaningful Words and Phrases (18 cases)
        meaningful_pairs = [
            ("book", "kobo", "Valid anagram with double 'o'."),
            ("coffee", "ffeeco", "Valid anagram with double 'f' and double 'e'."),
            ("mississippi", "ipssissipmi", "Complex word with 4 'i's, 4 's's, and 2 'p's."),
            ("astronomer", "moonstarer", "Classic multi-syllable anagram with identical counts."),
            ("statue", "astute", "6-letter valid anagram."),
            ("integral", "triangle", "8-letter mathematical word anagram."),
            ("reaction", "creation", "8-letter valid anagram."),
            ("admirer", "married", "Valid anagram with double 'r'."),
            ("teacher", "cheater", "7-letter anagram with repeated 'e'."),
            ("funeral", "realfun", "7-letter compound anagram."),
            ("orchestra", "carthorse", "9-letter classic anagram."),
            ("schoolmaster", "theclassroom", "Multi-syllable anagram test."),
            ("elevenplustwo", "twelveplusone", "Letter-exact mathematical phrase anagram."),
            ("conversation", "voicesranton", "Complex 12-letter anagram."),
            ("debitcard", "badcredit", "9-letter financial phrase anagram."),
            ("dormitory", "dirtyroom", "9-letter classic anagram."),
            ("theeyes", "theysee", "7-letter phrase anagram."),
            ("slotmachines", "cashlostinme", "Complex 12-letter anagram.")
        ]
        for s, t, r in meaningful_pairs:
            cases.append({
                "title": f"Meaningful Words: {s} vs {t}",
                "category": "Meaningful Words and Phrases",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 3. Inputs Designed to Expose Bugs (20 cases)
        # Exposes set() vs Counter() bugs, off-by-one errors, single substitutions
        bug_pairs = [
            ("aab", "abb", "Unique characters match {'a', 'b'}, but frequencies differ (2:1 vs 1:2). Exposes set() bugs."),
            ("aabbc", "abccc", "Unique characters match {'a', 'b', 'c'}, but counts differ. Exposes frequency bugs."),
            ("aabc", "abbc", "Exposes set-based anagram algorithms."),
            ("aaabbb", "aabbbb", "Equal length and same letters, but different frequency distribution."),
            ("xxyyzz", "xyyzzz", "Subtle count mismatch across 3 distinct characters."),
            ("mississippi", "misisipi", "Identical set of letters but different lengths. Exposes set comparison."),
            ("banana", "banan", "Off-by-one truncation bug."),
            ("banana", "bannna", "Same letters, same length, but count of 'n' differs."),
            ("apple", "papel", "Valid anagram containing duplicate 'p'."),
            ("apple", "appel", "Valid anagram with repeated letters."),
            ("aabbcc", "abcabc", "Same letter counts distributed differently."),
            ("1122", "1222", "Digit characters with unequal counts."),
            ("aaaabb", "aaabbb", "Subtle single-letter count difference."),
            ("pqpqpq", "qqpppq", "Valid anagram with alternating pattern."),
            ("rat", "car", "Same length, one character differs ('t' vs 'c')."),
            ("abcz", "abcy", "Off-by-one character at the end."),
            ("zabc", "yabc", "Off-by-one character at the beginning."),
            ("abcde", "abcdf", "Off-by-one mismatch at boundary index."),
            ("aabb", "bbaa", "Valid anagram with duplicate pairs."),
            ("anagram", "nagaram", "Standard anagram verification.")
        ]
        for s, t, r in bug_pairs:
            is_bug = (s in ["aab", "aabbc", "aabc", "aaabbb", "xxyyzz", "mississippi", "banana", "1122", "aaaabb"])
            cases.append({
                "title": f"Bug Hunter: {s} vs {t}",
                "category": "Inputs Designed to Expose Bugs",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": is_bug
            })

        # 4. Minimum and Maximum Boundary Values (18 cases)
        boundary_pairs = [
            ("triangle", "integral-s", "Unequal length strings must be rejected immediately."),
            ("a", "aa", "Single char vs double char."),
            ("ab", "abc", "Sub-string prefix mismatch."),
            ("abcd", "abcde", "Length difference by 1 character."),
            ("abcdef", "abcdefg", "Length difference of 1 at medium length."),
            ("short", "verylongstring", "Significantly different lengths."),
            ("prefix", "prefixsuffix", "Prefix extension."),
            ("x" * 50, "x" * 51, "Off-by-one boundary on longer strings."),
            ("az", "za", "Alphabetical extreme boundaries 'a' and 'z'."),
            ("a", "z", "Single character extreme alphabet boundary."),
            ("abcdefghijklmnopqrstuvwxyz", "zyxwvutsrqponmlkjihgfedcba", "Full 26-letter alphabet reversal."),
            ("aaa", "zzz", "Homogeneous strings at opposite ends of alphabet."),
            ("m", "m", "Single character middle of alphabet match."),
            ("x" * 100, "x" * 100, "100-character homogeneous string match."),
            ("x" * 100, "x" * 99 + "y", "100-character string with single character deviation."),
            ("z" * 100, "y" * 100, "100-character string with completely different letter."),
            ("a" * 50 + "b" * 50, "b" * 50 + "a" * 50, "100-character partitioned valid anagram."),
            ("a" * 50 + "b" * 50, "b" * 49 + "a" * 51, "100-character partitioned count deviation.")
        ]
        for s, t, r in boundary_pairs:
            cases.append({
                "title": f"Boundary Case: len({len(s)}) vs len({len(t)})",
                "category": "Minimum and Maximum Boundary Values",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 5. Empty and Single-Element Inputs (14 cases)
        empty_pairs = [
            ("", "", "Boundary: Both strings empty. Trivially valid anagram."),
            ("a", "a", "Boundary: Single identical character."),
            ("a", "b", "Boundary: Single non-identical character."),
            ("", "a", "Boundary: Empty string vs single character."),
            ("a", "", "Boundary: Single character vs empty string."),
            ("z", "z", "Boundary: Single end-of-alphabet character."),
            ("0", "0", "Boundary: Single numeric character."),
            (" ", " ", "Boundary: Single whitespace character."),
            ("x", "y", "Boundary: Single character mismatch."),
            ("1", "2", "Boundary: Single digit mismatch."),
            ("", "   ", "Boundary: Empty string vs whitespace string."),
            ("!", "!", "Boundary: Single punctuation symbol match."),
            ("?", "!", "Boundary: Single punctuation symbol mismatch."),
            ("#", "#", "Boundary: Single special character match.")
        ]
        for s, t, r in empty_pairs:
            cases.append({
                "title": f"Empty/Single Element: '{s}' vs '{t}'",
                "category": "Empty and Single-Element Inputs",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 6. Duplicate Values and Repeated Characters (16 cases)
        repeated_pairs = [
            ("aaaaa", "aaaa", "5 repeats vs 4 repeats. Length mismatch with identical character."),
            ("aaaa", "aaaa", "Identical 4-character repeated string."),
            ("bbbbbb", "bbbbbb", "Identical 6-character repeated string."),
            ("ababab", "bababa", "Alternating 2-character repeated pattern."),
            ("aabbcc", "ccbbaa", "Reversed duplicate pairs."),
            ("aaabbbccc", "cccbbbaaa", "Reversed duplicate triplets."),
            ("zzzzzz", "zzzzz", "Repeated boundary characters of unequal length."),
            ("111222", "222111", "Repeated numeric sequences."),
            ("banana", "nabana", "Multiple vowels and consonants in varied order."),
            ("papaya", "aappay", "Word with 3 'a's and 2 'p's."),
            ("pepper", "peperp", "Word with 3 'p's and 2 'e's."),
            ("assess", "sesass", "Word with 4 's's."),
            ("cocoon", "conoco", "Word with repeated 'c' and 'o'."),
            ("noon", "onon", "4-letter palindrome anagram."),
            ("deed", "eded", "Repeated letters with different order."),
            ("peep", "eepp", "Repeated letters with grouped order.")
        ]
        for s, t, r in repeated_pairs:
            cases.append({
                "title": f"Repeated Chars: '{s}' vs '{t}'",
                "category": "Duplicate Values and Repeated Characters",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 7. Special Characters, Whitespace, and Case Variations (16 cases)
        special_pairs = [
            ("Astronomer", "Moonstarer", "Mixed case variation."),
            ("Listen", "silent", "First letter capitalized."),
            ("Hello", "hello", "Capital letter mismatch."),
            ("A", "a", "Single character case sensitivity."),
            ("a b c", "c b a", "Strings containing space characters."),
            ("hello world", "world hello", "Phrase containing spaces."),
            ("foo-bar", "bar-foo", "Strings with hyphens."),
            ("test@123", "123@test", "Strings with '@' symbol and numbers."),
            ("!@#$%", "%$#@!", "Punctuation symbol anagram."),
            ("   ", "   ", "All whitespace characters."),
            (" a ", "a  ", "Asymmetric whitespace positioning."),
            ("tab\ttest", "test\ttab", "Strings containing tab characters."),
            ("Line1\nLine2", "Line2\nLine1", "Strings containing newline characters."),
            ("café", "féca", "Unicode accented characters."),
            ("c++", "+c+", "Programming language symbols."),
            ("C#&.NET", "NET.#&C", "Special symbol combinations.")
        ]
        for s, t, r in special_pairs:
            cases.append({
                "title": f"Special / Case: '{s}' vs '{t}'",
                "category": "Special Characters, Whitespace, and Case Variations",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 8. Negative Numbers, Zero, and Positive Numbers / Digits (12 cases)
        digit_pairs = [
            ("12345", "54321", "Permutation of digits 1-5."),
            ("9876543210", "0123456789", "All 10 decimal digits."),
            ("0", "0", "Single zero."),
            ("000", "0000", "Zero counts differing by 1."),
            ("-123", "321-", "Negative sign character included."),
            ("-5", "5-", "Negative sign and single digit."),
            ("+100", "001+", "Plus sign and digits."),
            ("100", "010", "Zero counts match."),
            ("010", "001", "Zero counts match."),
            ("102030", "302010", "Interleaved zeros and digits."),
            ("-100", "-010", "Negative symbol with matching digit counts."),
            ("999000", "000999", "Grouped digits and zeros.")
        ]
        for s, t, r in digit_pairs:
            cases.append({
                "title": f"Numeric Digits: '{s}' vs '{t}'",
                "category": "Negative Numbers, Zero, and Positive Numbers",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        # 9. Large Inputs for Performance Testing (10 cases)
        large_pairs = [
            ("a" * 1000 + "b" * 1000, "b" * 1000 + "a" * 1000, "2,000-character valid anagram."),
            ("a" * 2000, "a" * 2000, "2,000-character homogeneous valid anagram."),
            ("a" * 2000, "a" * 1999 + "b", "2,000-character string with single character deviation."),
            ("abc" * 500, "bca" * 500, "1,500-character 3-letter repeating anagram."),
            ("xyz" * 500, "zyx" * 500, "1,500-character 3-letter repeating anagram."),
            ("a" * 5000, "a" * 5000, "5,000-character large homogeneous string."),
            ("a" * 5000, "a" * 4999 + "c", "5,000-character string with 1 char mismatch."),
            ("abcdefghij" * 200, "jihgfedcba" * 200, "2,000-character 10-character cyclic anagram."),
            ("0123456789" * 300, "9876543210" * 300, "3,000-character numeric string anagram."),
            ("python" * 400, "nohtyp" * 400, "2,400-character repeated word anagram.")
        ]
        for s, t, r in large_pairs:
            cases.append({
                "title": f"Performance Scale: len={len(s)}",
                "category": "Large Inputs for Performance Testing",
                "inputs": {"s": s, "t": t},
                "reason": r,
                "is_bug_exposing": False
            })

        return cases

    @classmethod
    def _get_twosum_cases(cls) -> List[Dict[str, Any]]:
        cases = []

        # 1. Normal and Representative (20 cases)
        normal_configs = [
            ([2, 7, 11, 15], 9, "Standard positive integers at start indices [0, 1]."),
            ([1, 2, 3, 4, 5], 7, "Sum at indices [2, 3] (3 + 4 = 7)."),
            ([4, 8, 12, 16], 20, "Multiples of 4 (4 + 16 = 20)."),
            ([10, 20, 30, 40], 50, "Multiples of 10 (10 + 40 = 50 or 20 + 30 = 50)."),
            ([3, 5, 8, 13, 21], 16, "Fibonacci numbers (3 + 13 = 16)."),
            ([100, 200, 300], 500, "Hundreds summing to 500."),
            ([5, 10, 15, 20], 25, "Pair summing to 25."),
            ([7, 14, 21, 28], 35, "Multiples of 7."),
            ([1, 4, 6, 9], 10, "Pair (1 + 9 = 10) at extremes."),
            ([11, 22, 33], 55, "Indices [1, 2] summing to 55."),
            ([6, 7, 8, 9], 15, "Indices [0, 3] summing to 15."),
            ([2, 4, 6, 8, 10], 12, "Indices [0, 4] summing to 12."),
            ([1, 3, 5, 7, 9], 8, "Odd numbers summing to 8."),
            ([12, 15, 19, 21], 34, "Indices [1, 2] summing to 34."),
            ([50, 60, 70, 80], 130, "Indices [1, 2] summing to 130."),
            ([9, 13, 17, 21], 30, "Indices [0, 2] summing to 30."),
            ([14, 25, 36, 47], 61, "Indices [1, 2] summing to 61."),
            ([8, 16, 24, 32], 40, "Indices [0, 3] summing to 40."),
            ([20, 30, 40, 50], 70, "Indices [1, 2] summing to 70."),
            ([3, 6, 9, 12, 15], 18, "Indices [0, 4] summing to 18.")
        ]
        for nums, target, r in normal_configs:
            cases.append({
                "title": f"Normal Pair: Target {target}",
                "category": "Normal and Representative",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 2. Inputs Designed to Expose Bugs (20 cases)
        # Bug 1: Self-pairing bugs (target == 2 * nums[i] where nums[i] occurs only once)
        bug_configs = [
            ([3, 2, 4], 6, "Target 6 = 3 + 3. Exposes solutions reusing index 0 twice instead of [1, 2].", True),
            ([5, 1, 9], 10, "Target 10 = 5 + 5. Exposes self-pairing on element 5.", True),
            ([7, 3, 4], 14, "Target 14 = 7 + 7. Exposes self-pairing on element 7.", True),
            ([4, 1, 3], 8, "Target 8 = 4 + 4. Exposes self-pairing on element 4.", True),
            ([8, 5, 2], 16, "Target 16 = 8 + 8. Exposes self-pairing on element 8.", True),
            ([10, 3, 7], 20, "Target 20 = 10 + 10. Exposes self-pairing on element 10.", True),
            ([6, 2, 5, 1], 12, "Target 12 = 6 + 6. Exposes self-pairing on element 6.", True),
            ([1, 2, 8, 4], 16, "Target 16 = 8 + 8. Exposes self-pairing on element 8.", True),
            ([0, 1, 2], 0, "Target 0 = 0 + 0. Exposes self-pairing on zero.", True),
            ([12, 4, 8], 24, "Target 24 = 12 + 12. Exposes self-pairing on 12.", True),
            ([3, 3], 6, "Array contains two identical values at distinct indices [0, 1].", False),
            ([2, 5, 5, 11], 10, "Duplicate target elements in middle.", False),
            ([4, 4, 4], 8, "Multiple identical candidates.", False),
            ([1, 2, 3, 2], 4, "Repeated 2s summing to 4 with index separation.", False),
            ([0, 4, 3, 0], 0, "Two zeros summing to zero at extremes.", False),
            ([-2, -2], -4, "Duplicate negative values.", False),
            ([7, 7, 7, 7], 14, "All identical elements.", False),
            ([5, 1, 5], 10, "Duplicate values separated by 1.", False),
            ([9, 9], 18, "Minimal duplicate pair.", False),
            ([1, 1, 1], 2, "Duplicate ones.", False)
        ]
        for nums, target, r, is_bug in bug_configs:
            cases.append({
                "title": f"Bug Hunter: Target {target} with nums={nums}",
                "category": "Inputs Designed to Expose Bugs",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": is_bug
            })

        # 3. Minimum and Maximum Boundary Values (18 cases)
        boundary_configs = [
            ([5, 5], 10, "Smallest valid array size (2 elements)."),
            ([1, 2], 3, "Minimal array with consecutive elements."),
            ([10, 20], 30, "Minimal array with two elements."),
            ([100, -100], 0, "Minimal array cancelling to zero."),
            ([10, 20, 30, 40, 50], 60, "Pair spanning first and last indices (10 + 50 = 60)."),
            ([1, 9, 8, 7, 6, 5, 2], 3, "Pair at extreme boundaries [0, 6]."),
            ([1, 2, 3], 10, "Target not present. Should return empty list []."),
            ([5, 10, 15], 30, "Target larger than any pair sum."),
            ([2, 4, 6], 7, "Odd target with all even numbers."),
            ([10, 20], 100, "Target out of reach for two-element array."),
            ([0, 0], 1, "Target absent for zero array."),
            ([-5, -10], 0, "Negative array with zero target absent."),
            ([100, 200, 300], 1000, "Unreachable high target."),
            ([1, 3, 5, 7], 2, "Target smaller than minimum possible pair."),
            ([1000000, 2000000], 3000000, "Large integer values (10^6)."),
            ([-1000000, 1000000], 0, "Large magnitude opposite signs."),
            ([2147483640, 7], 2147483647, "32-bit signed integer maximum boundary."),
            ([-2147483648, 1], -2147483647, "32-bit signed integer minimum boundary.")
        ]
        for nums, target, r in boundary_configs:
            cases.append({
                "title": f"Boundary Case: Target {target}",
                "category": "Minimum and Maximum Boundary Values",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 4. Negative Numbers, Zero, and Positive Numbers (18 cases)
        neg_configs = [
            ([-3, 4, 3, 90], 0, "Negative and positive complement summing to 0."),
            ([-10, 20, -30, 40], 10, "Mixed signs summing to positive target."),
            ([-5, -4, -3, -2, -1], -7, "All negative array summing to negative target."),
            ([-50, 0, 50], 0, "Opposite extremes and zero."),
            ([-1, -2, -3, -4], -5, "Consecutive negatives."),
            ([-10, -20, 30], -30, "Negative pair summing to -30."),
            ([-15, 5, 10], -5, "Indices [0, 2] summing to -5."),
            ([0, 0], 0, "Two zeros summing to zero."),
            ([-1, 0, 1], 0, "Zero crossing pair."),
            ([-100, 50, 50], 100, "Positive target from duplicate positives."),
            ([0, 5, 10], 5, "Zero plus positive."),
            ([-7, 2, 5], -2, "Negative plus positive."),
            ([-8, -2, 10], 8, "Indices [1, 2] (-2 + 10 = 8)."),
            ([-12, -4, 0, 4, 12], 0, "Symmetric mixed signs."),
            ([-25, 25, 0], 0, "Zero pair with zero included."),
            ([-3, -6, -9], -15, "Indices [1, 2] summing to -15."),
            ([-1, 1], 0, "Minimal symmetric pair."),
            ([-4, 6, 2], 8, "Indices [1, 2] (6 + 2 = 8).")
        ]
        for nums, target, r in neg_configs:
            cases.append({
                "title": f"Negative / Zero: Target {target}",
                "category": "Negative Numbers, Zero, and Positive Numbers",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 5. Duplicate Values and Repeated Characters / Elements (14 cases)
        dup_configs = [
            ([1, 1, 1, 2, 7], 9, "Repeated 1s with distinct pair at end."),
            ([2, 2, 2, 2, 3, 4], 7, "Repeated 2s with distinct sum."),
            ([5, 5, 5, 5], 10, "Multiple identical candidates."),
            ([0, 1, 0, 2], 3, "Repeated zeros with target 3."),
            ([8, 8, 1, 2], 3, "Repeated 8s with target 3."),
            ([4, 4, 1, 4], 5, "Repeated 4s with target 5."),
            ([3, 1, 3, 4], 5, "Target 5 from [1, 4] with repeated 3s."),
            ([6, 2, 6, 3], 5, "Target 5 with repeated 6s."),
            ([9, 1, 9, 2], 3, "Target 3 with repeated 9s."),
            ([10, 10, 20, 30], 50, "Target 50 with repeated 10s."),
            ([2, 3, 3, 4], 6, "Target 6 formed by duplicate 3s."),
            ([7, 1, 7, 2], 9, "Target 9 formed by 7 and 2."),
            ([5, 2, 5, 3], 5, "Target 5 formed by 2 and 3."),
            ([1, 1, 2, 2], 3, "Target 3 formed by 1 and 2.")
        ]
        for nums, target, r in dup_configs:
            cases.append({
                "title": f"Duplicate Elements: Target {target}",
                "category": "Duplicate Values and Repeated Characters",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 6. Large Inputs for Performance Testing (10 cases)
        large_configs = [
            (list(range(1, 101)), 199, "100-element sequential array."),
            (list(range(1, 501)), 999, "500-element sequential array."),
            (list(range(1, 1001)), 1999, "1,000-element sequential array."),
            (list(range(1, 1001)), 5000, "1,000-element array with no solution."),
            ([-x for x in range(1, 1001)], -1999, "1,000 negative integers."),
            ([10] * 500 + [20, 30], 50, "502-element array with duplicates and pair at end."),
            ([0] * 998 + [1, 2], 3, "1,000 elements with solution at final indices."),
            ([x * 2 for x in range(1, 251)], 500, "250 even numbers."),
            ([x * 3 for x in range(1, 351)], 1050, "350 multiples of 3."),
            (list(range(1000, 2000)), 3997, "1,000 large range numbers.")
        ]
        for nums, target, r in large_configs:
            cases.append({
                "title": f"Performance Scale: len={len(nums)}, Target={target}",
                "category": "Large Inputs for Performance Testing",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 7. Empty and Single-Element Inputs / Boundaries (8 cases)
        edge_configs = [
            ([], 0, "Empty array boundary. Returns []."),
            ([1], 1, "Single element insufficient for pair. Returns []."),
            ([42], 84, "Single element equal to target/2. Returns []."),
            ([0], 0, "Single zero. Returns []."),
            ([-5], -5, "Single negative element. Returns []."),
            ([99], 100, "Single element. Returns []."),
            ([], 5, "Empty array with positive target."),
            ([7], 14, "Single element target match check.")
        ]
        for nums, target, r in edge_configs:
            cases.append({
                "title": f"Edge Array: len={len(nums)}, Target={target}",
                "category": "Empty and Single-Element Inputs",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 8. Meaningful Sequences and Combinations (12 cases)
        math_configs = [
            ([1, 1, 2, 3, 5, 8, 13], 21, "Fibonacci sequence numbers (8 + 13 = 21)."),
            ([2, 3, 5, 7, 11, 13, 17], 20, "Prime numbers sequence (7 + 13 = 20 or 3 + 17 = 20)."),
            ([1, 2, 4, 8, 16, 32], 18, "Powers of 2 (2 + 16 = 18)."),
            ([1, 4, 9, 16, 25, 36], 40, "Square numbers sequence (4 + 36 = 40)."),
            ([10, 20, 30, 40, 50, 60], 70, "Arithmetic sequence (10 + 60 = 70)."),
            ([1, -1, 2, -2, 3, -3], 1, "Alternating sign sequence (3 + -2 = 1)."),
            ([9, 8, 7, 6, 5, 4], 11, "Consecutive descending sequence (7 + 4 = 11)."),
            ([5, 15, 25, 35, 45], 50, "Stepped increment sequence (5 + 45 = 50)."),
            ([100, 101, 102, 103], 203, "Close values sequence (100 + 103 = 203)."),
            ([1, 100000], 100001, "Large gap sequence."),
            ([3, 1000, 7, 2000], 10, "Mixed magnitude values (3 + 7 = 10)."),
            ([0, 50, 100], 150, "Zero offset sequence (50 + 100 = 150).")
        ]
        for nums, target, r in math_configs:
            cases.append({
                "title": f"Structured Math Sequence: Target {target}",
                "category": "Meaningful Words and Phrases",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        return cases

    @classmethod
    def _get_palindrome_cases(cls) -> List[Dict[str, Any]]:
        cases = []

        # 1. Normal and Representative (20 cases)
        words = [
            ("racecar", True, "Classic odd-length symmetric word."),
            ("madam", True, "5-letter valid palindrome."),
            ("level", True, "5-letter palindrome with repeated 'e'."),
            ("rotor", True, "5-letter mechanical word palindrome."),
            ("kayak", True, "5-letter sports palindrome."),
            ("reviver", True, "7-letter palindrome."),
            ("noon", True, "4-letter even-length palindrome."),
            ("civic", True, "5-letter palindrome."),
            ("radar", True, "5-letter palindrome."),
            ("stats", True, "5-letter palindrome."),
            ("tenet", True, "5-letter palindrome."),
            ("python", False, "Standard non-palindrome lowercase word."),
            ("software", False, "Standard non-palindrome word."),
            ("algorithm", False, "Standard non-palindrome word."),
            ("computer", False, "Standard non-palindrome word."),
            ("testing", False, "Standard non-palindrome word."),
            ("developer", False, "Non-palindrome word with repeated letters."),
            ("program", False, "Standard non-palindrome word."),
            ("deed", True, "4-letter even palindrome."),
            ("peep", True, "4-letter even palindrome.")
        ]
        for s, exp, r in words:
            cases.append({
                "title": f"Word Check: '{s}'",
                "category": "Normal and Representative",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": False
            })

        # 2. Inputs Designed to Expose Bugs (18 cases)
        # Exposes failure to sanitize punctuation, spaces, or mixed casing
        bug_phrases = [
            ("A man, a plan, a canal: Panama", "Classic phrase palindrome. Exposes missing punctuation and space stripping.", True),
            ("Was it a car or a cat I saw?", "Phrase with question mark and spaces.", True),
            ("No 'x' in Nixon", "Phrase with apostrophe and capital letter.", True),
            ("Madam, in Eden, I'm Adam", "Classic phrase with multiple punctuation marks.", True),
            ("Never odd or even", "Phrase with spaces and even-length symmetry.", True),
            ("Step on no pets", "Sentence reading backwards identical.", True),
            ("Live on time, emit no evil", "Punctuation and space sentence palindrome.", True),
            ("Red rum, sir, is murder", "Classic phrase palindrome.", True),
            ("Doc, note: I dissent. A fast never prevents a fatness. I diet on cod.", "Complex paragraph palindrome.", True),
            ("Able was I ere I saw Elba", "Historical sentence palindrome.", True),
            ("RaceCar", "Case-sensitive variation.", False),
            ("Madam", "First letter capitalized.", False),
            ("KaYak", "CamelCase palindrome.", False),
            ("NoOn", "Mixed case even palindrome.", False),
            ("abccba", "Even-length pure palindrome.", False),
            ("abcdcba", "Odd-length pure palindrome.", False),
            ("ab", "Two-character non-palindrome.", False),
            ("ba", "Two-character non-palindrome.", False)
        ]
        for s, r, is_bug in bug_phrases:
            cases.append({
                "title": f"Bug Hunter: '{s[:25]}...'",
                "category": "Inputs Designed to Expose Bugs",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": is_bug
            })

        # 3. Minimum and Maximum Boundary Values (16 cases)
        boundary_strings = [
            ("a", "Single character minimum boundary. Trivially symmetric."),
            ("z", "Single end-of-alphabet character."),
            ("0", "Single digit character."),
            ("aa", "Two identical characters."),
            ("ab", "Two different characters."),
            ("aba", "Minimal 3-character palindrome."),
            ("abc", "Minimal 3-character non-palindrome."),
            ("a" * 50, "50 identical characters."),
            ("a" * 49 + "b", "50 characters with asymmetric end."),
            ("b" + "a" * 49, "50 characters with asymmetric start."),
            ("a" * 25 + "b" + "a" * 25, "51 characters with center element."),
            ("a" * 25 + "bc" + "a" * 25, "52 characters with asymmetric center."),
            ("az", "Extreme alphabet boundaries."),
            ("aza", "Extreme alphabet boundaries with center match."),
            ("z" * 100, "100 identical characters."),
            ("z" * 99 + "a", "100 characters with 1 mismatch.")
        ]
        for s, r in boundary_strings:
            cases.append({
                "title": f"Boundary: len={len(s)}",
                "category": "Minimum and Maximum Boundary Values",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": False
            })

        # 4. Empty and Single-Element Inputs (14 cases)
        empty_strings = [
            ("", "Empty string boundary. Trivially a palindrome."),
            (" ", "Single space character."),
            ("   ", "Multiple space characters."),
            ("\t", "Single tab character."),
            ("\n", "Single newline character."),
            (".", "Single period."),
            ("!", "Single exclamation mark."),
            ("?", "Single question mark."),
            ("-", "Single hyphen."),
            ("x", "Single lowercase letter."),
            ("Y", "Single uppercase letter."),
            ("9", "Single numeric digit."),
            ("#", "Single symbol."),
            ("@", "Single at-sign.")
        ]
        for s, r in empty_strings:
            cases.append({
                "title": f"Empty/Single: '{s}'",
                "category": "Empty and Single-Element Inputs",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": False
            })

        # 5. Special Characters, Whitespace, and Case Variations (16 cases)
        special_cases = [
            (" ,.;:!?", "Only non-alphanumeric characters. Reduces to empty after filtering."),
            ("!@#$%^&*()", "Symbol-only string."),
            ("---", "Hyphen-only string."),
            ("12321", "Numeric palindrome."),
            ("12345", "Numeric non-palindrome."),
            ("1001", "Even-length numeric palindrome."),
            ("10", "Two-digit numeric non-palindrome."),
            ("0110", "Zero-padded numeric palindrome."),
            ("A1B2B1A", "Alphanumeric palindrome."),
            ("A1B2C1A", "Alphanumeric non-palindrome."),
            ("Top spot", "Two words palindrome."),
            ("My gym", "Two words with spaces."),
            ("Don't nod", "Sentence with contraction apostrophe."),
            ("I did, did I?", "Sentence palindrome."),
            ("Evil olive", "Food-themed phrase palindrome."),
            ("Borrow or rob?", "Crime-themed sentence palindrome.")
        ]
        for s, r in special_cases:
            cases.append({
                "title": f"Special/Punctuation: '{s}'",
                "category": "Special Characters, Whitespace, and Case Variations",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": False
            })

        # 6. Duplicate Values and Repeated Characters (14 cases)
        repeated_strings = [
            ("aaaaaa", "Even number of identical characters."),
            ("aaaaaaa", "Odd number of identical characters."),
            ("bbbbbbbb", "8 repeated 'b's."),
            ("abababa", "Alternating odd palindrome."),
            ("abababab", "Alternating even non-palindrome."),
            ("aabbccbbaa", "Nested symmetric pairs."),
            ("aaabbbcccbbbaaa", "Nested symmetric triplets."),
            ("111111", "Repeated digit palindrome."),
            ("1112111", "Repeated digit with center deviation."),
            ("22222", "5 repeated '2's."),
            ("xxxxxxxxx", "9 repeated 'x's."),
            ("radar radar", "Repeated palindrome words with space."),
            ("noon noon", "Repeated even palindromes with space."),
            ("deed deed", "Repeated deed with space.")
        ]
        for s, r in repeated_strings:
            cases.append({
                "title": f"Repeated Chars: '{s}'",
                "category": "Duplicate Values and Repeated Characters",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": False
            })

        # 7. Large Inputs for Performance Testing (10 cases)
        large_cases = [
            ("ab" * 500 + "c" + "ba" * 500, "1,001-character symmetric sequence."),
            ("a" * 2000, "2,000-character homogeneous palindrome."),
            ("a" * 1999 + "b", "2,000-character string with 1 char mismatch."),
            ("racecar" * 200, "1,400-character repeated palindrome."),
            ("abcdefghij" * 100 + "jihgfedcba" * 100, "2,000-character structured palindrome."),
            ("x" * 5000, "5,000-character homogeneous string."),
            ("x" * 2500 + "y" + "x" * 2500, "5,001-character symmetric string."),
            ("x" * 2500 + "yz" + "x" * 2500, "5,002-character asymmetric center string."),
            ("1234567890" * 200 + "0987654321" * 200, "4,000-character numeric palindrome."),
            ("madam" * 300, "1,500-character multi-word palindrome.")
        ]
        for s, r in large_cases:
            cases.append({
                "title": f"Performance Scale: len={len(s)}",
                "category": "Large Inputs for Performance Testing",
                "inputs": {"s": s},
                "reason": r,
                "is_bug_exposing": False
            })

        return cases

    @classmethod
    def _get_binarysearch_cases(cls) -> List[Dict[str, Any]]:
        cases = []

        # 1. Normal and Representative (20 cases)
        normal_searches = [
            ([1, 3, 5, 7, 9, 11], 5, "Target sits in middle of array."),
            ([1, 3, 5, 7, 9, 11], 1, "Target at index 0."),
            ([1, 3, 5, 7, 9, 11], 11, "Target at final index."),
            ([2, 4, 6, 8, 10], 6, "Target in exact middle of odd-length array."),
            ([2, 4, 6, 8, 10], 4, "Target at index 1."),
            ([2, 4, 6, 8, 10], 8, "Target at index 3."),
            ([10, 20, 30, 40, 50, 60], 30, "Target in left-middle."),
            ([10, 20, 30, 40, 50, 60], 40, "Target in right-middle."),
            ([5, 10, 15, 20, 25], 15, "Target in center of 5 elements."),
            ([100, 200, 300, 400], 200, "Target at index 1 of 4 elements."),
            ([1, 2, 3, 4, 5, 6, 7], 4, "Middle of 7 elements."),
            ([1, 2, 3, 4, 5, 6, 7], 2, "Quarter mark."),
            ([1, 2, 3, 4, 5, 6, 7], 6, "Three-quarter mark."),
            ([8, 16, 24, 32, 40, 48], 24, "Multiples of 8."),
            ([3, 6, 9, 12, 15, 18, 21], 12, "Multiples of 3."),
            ([11, 22, 33, 44, 55], 33, "Multiples of 11."),
            ([7, 14, 21, 28, 35], 21, "Multiples of 7."),
            ([15, 30, 45, 60, 75], 45, "Multiples of 15."),
            ([4, 8, 12, 16, 20], 8, "Multiples of 4."),
            ([50, 100, 150, 200], 150, "Multiples of 50.")
        ]
        for nums, target, r in normal_searches:
            cases.append({
                "title": f"Search Found: Target {target} in len={len(nums)}",
                "category": "Normal and Representative",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 2. Inputs Designed to Expose Bugs (18 cases)
        # Bug 1: Off-by-one loops like 'while left < right' that fail on single element arrays
        bug_searches = [
            ([42], 42, "Single-element array target present. Exposes off-by-one 'while left < right' loop bugs.", True),
            ([100], 100, "Single-element array target present.", True),
            ([0], 0, "Single zero array target present.", True),
            ([-5], -5, "Single negative element target present.", True),
            ([1, 2], 2, "Two-element array target at rightmost index. Exposes right-pointer truncation.", True),
            ([1, 2], 1, "Two-element array target at leftmost index.", False),
            ([10, 20, 30, 40], 40, "Target at right boundary index len-1.", False),
            ([10, 20, 30, 40], 10, "Target at left boundary index 0.", False),
            ([1, 3, 5], 3, "Target in exact middle.", False),
            ([1, 3, 5], 1, "Target at left.", False),
            ([1, 3, 5], 5, "Target at right.", False),
            ([2, 5, 8, 12], 2, "Boundary index 0 in 4 elements.", False),
            ([2, 5, 8, 12], 12, "Boundary index 3 in 4 elements.", False),
            ([4, 7, 9, 14, 18], 18, "Boundary index 4 in 5 elements.", False),
            ([4, 7, 9, 14, 18], 4, "Boundary index 0 in 5 elements.", False),
            ([1, 2, 3], 2, "Middle element.", False),
            ([1, 2, 3, 4], 3, "Right-leaning middle element.", False),
            ([1, 2, 3, 4], 2, "Left-leaning middle element.", False)
        ]
        for nums, target, r, is_bug in bug_searches:
            cases.append({
                "title": f"Bug Hunter: Target {target} in {nums}",
                "category": "Inputs Designed to Expose Bugs",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": is_bug
            })

        # 3. Minimum and Maximum Boundary Values (18 cases)
        # Targets absent (smaller than min, larger than max, in-between)
        absent_searches = [
            ([10, 20, 30], 5, "Target smaller than minimum. Expected -1."),
            ([10, 20, 30], 50, "Target larger than maximum. Expected -1."),
            ([10, 20, 30], 15, "Target in between elements. Expected -1."),
            ([10, 20, 30], 25, "Target in between upper elements. Expected -1."),
            ([1, 5, 9, 13], 0, "Target below lower bound. Expected -1."),
            ([1, 5, 9, 13], 15, "Target above upper bound. Expected -1."),
            ([1, 5, 9, 13], 3, "Target between index 0 and 1. Expected -1."),
            ([1, 5, 9, 13], 7, "Target between index 1 and 2. Expected -1."),
            ([1, 5, 9, 13], 11, "Target between index 2 and 3. Expected -1."),
            ([100], 50, "Single-element array target smaller. Expected -1."),
            ([100], 150, "Single-element array target larger. Expected -1."),
            ([1, 2], 0, "Two-element array target smaller. Expected -1."),
            ([1, 2], 3, "Two-element array target larger. Expected -1."),
            ([10, 30], 20, "Two-element array target in between. Expected -1."),
            ([2, 4, 6, 8, 10], 1, "Absent target smaller than all. Expected -1."),
            ([2, 4, 6, 8, 10], 11, "Absent target larger than all. Expected -1."),
            ([2, 4, 6, 8, 10], 5, "Absent target in middle gap. Expected -1."),
            ([2, 4, 6, 8, 10], 7, "Absent target in upper gap. Expected -1.")
        ]
        for nums, target, r in absent_searches:
            cases.append({
                "title": f"Target Absent: Target {target} in len={len(nums)}",
                "category": "Minimum and Maximum Boundary Values",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 4. Empty and Single-Element Inputs (10 cases)
        edge_searches = [
            ([], 1, "Empty array search. Expected -1."),
            ([], 0, "Empty array with zero target. Expected -1."),
            ([], -1, "Empty array with negative target. Expected -1."),
            ([5], 5, "Single element match."),
            ([5], 6, "Single element mismatch."),
            ([0], 0, "Single zero match."),
            ([0], 1, "Single zero mismatch."),
            ([-10], -10, "Single negative match."),
            ([-10], 0, "Single negative mismatch."),
            ([999], 999, "Single large element match.")
        ]
        for nums, target, r in edge_searches:
            cases.append({
                "title": f"Empty / Single: Target {target} in len={len(nums)}",
                "category": "Empty and Single-Element Inputs",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 5. Negative Numbers, Zero, and Positive Numbers (16 cases)
        neg_searches = [
            ([-50, -20, -5, 0, 15, 30], -5, "Sorted array crossing negative numbers and zero."),
            ([-50, -20, -5, 0, 15, 30], 0, "Target is zero in negative/positive array."),
            ([-50, -20, -5, 0, 15, 30], -50, "Target is most negative element."),
            ([-50, -20, -5, 0, 15, 30], 30, "Target is most positive element."),
            ([-100, -50, -25, -10], -25, "All negative sorted array."),
            ([-100, -50, -25, -10], -100, "Left boundary in all negative array."),
            ([-100, -50, -25, -10], -10, "Right boundary in all negative array."),
            ([-10, -5, 0, 5, 10], 0, "Symmetric negative/positive around zero."),
            ([-10, -5, 0, 5, 10], -5, "Left negative element."),
            ([-10, -5, 0, 5, 10], 5, "Right positive element."),
            ([-20, -15, -10, -5], -15, "Pure negative array."),
            ([-30, -20, -10], -20, "Middle negative element."),
            ([-5, 0, 5], 0, "Minimal zero crossing."),
            ([-1, 0, 1], -1, "Minimal negative index 0."),
            ([-1, 0, 1], 1, "Minimal positive index 2."),
            ([-100, 0, 100], 0, "Wide zero crossing.")
        ]
        for nums, target, r in neg_searches:
            cases.append({
                "title": f"Negative / Zero: Target {target}",
                "category": "Negative Numbers, Zero, and Positive Numbers",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 6. Large Inputs for Performance Testing (10 cases)
        large_searches = [
            (list(range(1, 101)), 50, "100-element array target in middle."),
            (list(range(1, 101)), 1, "100-element array target at start."),
            (list(range(1, 101)), 100, "100-element array target at end."),
            (list(range(1, 501)), 250, "500-element array target in middle."),
            (list(range(1, 1001)), 750, "1,000-element array target at 3/4 index."),
            (list(range(1, 1001)), 1001, "1,000-element array target absent."),
            (list(range(1, 1001)), 0, "1,000-element array target below minimum."),
            ([x * 2 for x in range(1, 501)], 500, "500 even numbers."),
            ([x * 3 for x in range(1, 351)], 300, "350 multiples of 3."),
            (list(range(-500, 501)), 0, "1,001 mixed signed integers target 0.")
        ]
        for nums, target, r in large_searches:
            cases.append({
                "title": f"Performance Scale: len={len(nums)}, Target={target}",
                "category": "Large Inputs for Performance Testing",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        # 7. Duplicate Values and Repeated Characters / Sequences (12 cases)
        dup_searches = [
            ([1, 2, 2, 2, 3], 2, "Array with multiple duplicate target elements."),
            ([2, 2, 2, 2], 2, "All elements identical to target."),
            ([1, 1, 3, 3, 5, 5], 3, "Pair duplicates target 3."),
            ([0, 0, 1, 1], 0, "Target at zero duplicates."),
            ([0, 0, 1, 1], 1, "Target at one duplicates."),
            ([5, 5, 5, 5, 5], 5, "5 identical elements."),
            ([10, 10, 20, 20], 10, "Target 10 in duplicate pairs."),
            ([10, 10, 20, 20], 20, "Target 20 in duplicate pairs."),
            ([1, 1, 1, 2], 1, "Dominant duplicates at left."),
            ([1, 2, 2, 2], 2, "Dominant duplicates at right."),
            ([3, 3, 3, 4, 4, 4], 3, "Multiple clusters target left cluster."),
            ([3, 3, 3, 4, 4, 4], 4, "Multiple clusters target right cluster.")
        ]
        for nums, target, r in dup_searches:
            cases.append({
                "title": f"Duplicate Array: Target {target}",
                "category": "Duplicate Values and Repeated Characters",
                "inputs": {"nums": nums, "target": target},
                "reason": r,
                "is_bug_exposing": False
            })

        return cases

    @classmethod
    def _get_average_cases(cls, pname: str) -> List[Dict[str, Any]]:
        cases = []

        # 1. Normal and Representative (20 cases)
        lists = [
            ([10, 20, 30, 40, 50], "Standard positive integer list with integer mean 30.0."),
            ([1, 2, 3, 4, 5], "Sequential numbers 1-5, mean 3.0."),
            ([2, 4, 6, 8, 10], "Even numbers, mean 6.0."),
            ([1, 3, 5, 7, 9], "Odd numbers, mean 5.0."),
            ([5, 10, 15, 20], "Multiples of 5, mean 12.5."),
            ([100, 200, 300], "Hundreds, mean 200.0."),
            ([10, 20], "Two elements, mean 15.0."),
            ([1, 2], "Two elements, float mean 1.5."),
            ([7, 14, 21], "Multiples of 7, mean 14.0."),
            ([8, 16, 24, 32], "Multiples of 8, mean 20.0."),
            ([3, 6, 9, 12], "Multiples of 3, mean 7.5."),
            ([15, 25, 35], "Numbers ending in 5, mean 25.0."),
            ([50, 100, 150, 200], "Fifty increments, mean 125.0."),
            ([4, 8, 12, 16], "Multiples of 4, mean 10.0."),
            ([11, 22, 33], "Multiples of 11, mean 22.0."),
            ([20, 30, 40], "Decade numbers, mean 30.0."),
            ([12, 18, 24], "Six increments, mean 18.0."),
            ([9, 18, 27], "Multiples of 9, mean 18.0."),
            ([1, 4, 9, 16], "Squares, mean 7.5."),
            ([2, 3, 5, 7, 11], "Primes, mean 5.6.")
        ]
        for nums, r in lists:
            cases.append({
                "title": f"Normal Average: len={len(nums)}",
                "category": "Normal and Representative",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": False
            })

        # 2. Inputs Designed to Expose Bugs (15 cases)
        # Empty list is prime bug hunter for ZeroDivisionError
        bug_lists = [
            ([], "Empty list input. Exposes missing guard for ZeroDivisionError when dividing by len().", True),
            ([0], "Single zero element. Exposes zero-truthiness bugs (if not nums: ...).", True),
            ([0, 0, 0], "All zeros list. Mean is 0.0.", False),
            ([0, 0, 0, 0, 0], "Multiple zeros.", False),
            ([-5, 5], "Opposites summing to 0.", False),
            ([-10, 10], "Opposites summing to 0.", False),
            ([-100, 100], "Large opposites summing to 0.", False),
            ([-1, 0, 1], "Symmetric around zero, mean 0.0.", False),
            ([1], "Single positive element, mean 1.0.", False),
            ([42], "Single element boundary.", False),
            ([-42], "Single negative element boundary.", False),
            ([100], "Single hundred boundary.", False),
            ([1e-5, 1e-5], "Very small floating numbers.", False),
            ([1000000, 2000000], "Large integers.", False),
            ([0, 10], "Zero and positive, mean 5.0.", False)
        ]
        for nums, r, is_bug in bug_lists:
            cases.append({
                "title": f"Bug Hunter: len={len(nums)}",
                "category": "Inputs Designed to Expose Bugs",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": is_bug
            })

        # 3. Minimum and Maximum Boundary Values (18 cases)
        boundary_lists = [
            ([99], "Single element boundary."),
            ([-99], "Single negative boundary."),
            ([0], "Single zero boundary."),
            ([2147483647], "Max 32-bit integer."),
            ([-2147483648], "Min 32-bit integer."),
            ([1000000000, 2000000000], "Billion magnitude numbers."),
            ([-1000000000, 1000000000], "Billion magnitude cancellation."),
            ([1, 1], "Two identical ones."),
            ([10, 10], "Two identical tens."),
            ([100, 100, 100], "Three identical hundreds."),
            ([5, 5, 5, 5, 5], "Five identical fives."),
            ([0.5, 1.5, 2.5], "Floating point boundary."),
            ([0.1, 0.2, 0.3], "Small floating point precision."),
            ([1.0, 2.0, 3.0], "Explicit float values."),
            ([10.5, 20.5], "Mixed float addition."),
            ([-0.5, 0.5], "Floating cancellation."),
            ([100, -100, 200, -200], "Two cancelling pairs."),
            ([1, 1000], "Wide spread two elements.")
        ]
        for nums, r in boundary_lists:
            cases.append({
                "title": f"Boundary List: len={len(nums)}",
                "category": "Minimum and Maximum Boundary Values",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": False
            })

        # 4. Negative Numbers, Zero, and Positive Numbers (18 cases)
        neg_lists = [
            ([-10, 0, 10], "Symmetric negative, zero, positive."),
            ([-5, -10, -15], "All negative numbers."),
            ([-1, -2, -3, -4, -5], "Consecutive negatives, mean -3.0."),
            ([-20, -40, -60], "Even negatives."),
            ([-10, 20, -30, 40], "Alternating signs."),
            ([-100, -200, -300], "Hundreds negatives."),
            ([-1, 1, -1, 1], "Alternating ones."),
            ([-2, 2, -2, 2], "Alternating twos."),
            ([-50, 0, 50, 0], "Zeros and cancellation."),
            ([-10, -5, 0, 5, 10], "5-element symmetric sequence."),
            ([-7, -14, -21], "Multiples of -7."),
            ([-15, 0, 15], "15 increments."),
            ([-3, -6, -9, 0], "Mixed negatives with zero."),
            ([-8, -4, 0, 4, 8], "Even symmetric sequence."),
            ([-25, 25, -25, 25], "Oscillating values."),
            ([-12, 6, 0], "Mixed negative and positive."),
            ([-100, 50], "Negative dominance, mean -25.0."),
            ([-50, 100], "Positive dominance, mean 25.0.")
        ]
        for nums, r in neg_lists:
            cases.append({
                "title": f"Negative / Zero: len={len(nums)}",
                "category": "Negative Numbers, Zero, and Positive Numbers",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": False
            })

        # 5. Duplicate Values and Repeated Characters / Elements (16 cases)
        dup_lists = [
            ([7, 7, 7, 7, 7, 7, 7], "All identical elements (mean equals the element)."),
            ([2, 2, 2, 2], "Repeated twos."),
            ([3, 3, 3, 3, 3], "Repeated threes."),
            ([10, 10, 10, 10], "Repeated tens."),
            ([5, 5, 10, 10], "Pairs of duplicates."),
            ([1, 1, 2, 2, 3, 3], "Triplets of duplicates."),
            ([0, 0, 1, 1], "Zeros and ones pairs."),
            ([8, 8, 8], "Three eights."),
            ([4, 4, 4, 4, 4], "Five fours."),
            ([9, 9], "Two nines."),
            ([12, 12, 12], "Three twelves."),
            ([15, 15, 15, 15], "Four fifteens."),
            ([20, 20, 30, 30], "Two pairs."),
            ([100, 100, 200, 200], "Hundreds pairs."),
            ([1, 1, 1, 1, 1, 1, 1, 1], "Eight ones."),
            ([6, 6, 6, 6], "Four sixes.")
        ]
        for nums, r in dup_lists:
            cases.append({
                "title": f"Duplicates: len={len(nums)}",
                "category": "Duplicate Values and Repeated Characters",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": False
            })

        # 6. Large Inputs for Performance Testing (10 cases)
        large_lists = [
            (list(range(1, 101)), "100 sequential integers, mean 50.5."),
            (list(range(1, 501)), "500 sequential integers, mean 250.5."),
            (list(range(1, 1001)), "1,000 sequential integers, mean 500.5."),
            ([10] * 1000, "1,000 identical numbers, mean 10.0."),
            ([0] * 1000, "1,000 zeros, mean 0.0."),
            ([-x for x in range(1, 1001)], "1,000 negative integers."),
            ([1, -1] * 500, "1,000 alternating values, mean 0.0."),
            ([x * 2 for x in range(1, 501)], "500 even numbers."),
            ([100] * 500 + [200] * 500, "1,000 partitioned numbers, mean 150.0."),
            (list(range(-500, 501)), "1,001 symmetric integers, mean 0.0.")
        ]
        for nums, r in large_lists:
            cases.append({
                "title": f"Performance Scale: len={len(nums)}",
                "category": "Large Inputs for Performance Testing",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": False
            })

        # 7. Empty and Single-Element Inputs (8 cases)
        single_lists = [
            ([0], "Single zero element."),
            ([1], "Single 1."),
            ([-1], "Single -1."),
            ([10], "Single 10."),
            ([-10], "Single -10."),
            ([100], "Single 100."),
            ([0.5], "Single float 0.5."),
            ([9999], "Single large number.")
        ]
        for nums, r in single_lists:
            cases.append({
                "title": f"Single Element: {nums}",
                "category": "Empty and Single-Element Inputs",
                "inputs": {pname: nums},
                "reason": r,
                "is_bug_exposing": False
            })

        return cases

    @classmethod
    def _get_generic_synthesized_cases(cls, analysis: CodeAnalysis, target_count: int = 105) -> List[Dict[str, Any]]:
        """
        Synthesizes a rich suite of categorized test cases for ANY arbitrary user function
        based on parameter signatures, types, and mathematical boundary domains.
        Guarantees minimum 100 test cases.
        """
        params = analysis.input_parameters
        if not params:
            # Fallback parameter if none detected
            from .models import ParameterInfo
            params = [ParameterInfo(name="input_val", type_name="int")]

        cases = []
        pnames = [p.name for p in params]

        # Domain generator per parameter
        def get_domain_for_param(param_info):
            t = param_info.type_name.lower()
            if "int" in t:
                return [
                    ("Normal", [1, 2, 5, 10, 15, 20, 25, 42, 50, 100]),
                    ("Boundary", [0, -1, 1, 2147483647, -2147483648, 1000, -1000]),
                    ("Empty/Single", [0, 1, -1]),
                    ("Duplicates", [2, 2, 5, 5, 10, 10]),
                    ("Negative", [-1, -2, -5, -10, -20, -50, -100]),
                    ("Large", [10000, 50000, 100000])
                ]
            elif "float" in t:
                return [
                    ("Normal", [1.5, 2.5, 3.14159, 10.0, 25.5, 0.5]),
                    ("Boundary", [0.0, -0.0, 1e-5, -1e-5, 1e6, -1e6]),
                    ("Empty/Single", [0.0, 1.0, -1.0]),
                    ("Duplicates", [2.5, 2.5, 0.5, 0.5]),
                    ("Negative", [-1.5, -2.5, -3.14, -10.0]),
                    ("Large", [999999.99, -999999.99])
                ]
            elif "str" in t:
                return [
                    ("Normal", ["hello", "world", "test", "example", "code", "python", "developer", "solution"]),
                    ("Boundary", ["a", "z", "a" * 50, "a" * 100, "abcdefghijklmnopqrstuvwxyz"]),
                    ("Empty/Single", ["", "a", " ", "\t", "0"]),
                    ("Duplicates", ["aaaaa", "ababab", "banana", "coffee", "book"]),
                    ("Special", ["!@#$%", "hello world", "foo-bar", "test@123", "   "]),
                    ("Large", ["a" * 500, "abc" * 200, "word" * 250])
                ]
            elif "list" in t or "[" in t or "vector" in t or "array" in t:
                return [
                    ("Normal", [[1, 2, 3], [4, 5, 6], [10, 20, 30], [2, 7, 11, 15], list(range(5))]),
                    ("Boundary", [[], [0], [1], [-1], [100], [2147483647]]),
                    ("Empty/Single", [[], [42], [0]]),
                    ("Duplicates", [[1, 1, 1], [2, 2, 3, 3], [0, 0, 0, 0], [5, 5]]),
                    ("Negative", [[-1, -2, -3], [-10, 0, 10], [-5, 5]]),
                    ("Large", [list(range(50)), list(range(100)), [1] * 100])
                ]
            elif "bool" in t:
                return [
                    ("Normal", [True, False, True, False]),
                    ("Boundary", [True, False]),
                    ("Empty/Single", [False, True]),
                    ("Duplicates", [True, True, False, False]),
                    ("Negative", [False, True]),
                    ("Large", [True, False])
                ]
            else:
                return [
                    ("Normal", [1, 2, 3, 4, 5]),
                    ("Boundary", [0, -1, 100]),
                    ("Empty/Single", [0, 1]),
                    ("Duplicates", [2, 2, 3, 3]),
                    ("Negative", [-1, -2, -5]),
                    ("Large", [1000, 2000])
                ]

        # Candidate matrix per parameter
        param_domains = {p.name: get_domain_for_param(p) for p in params}

        # Categories to cover
        category_map = [
            ("Normal and Representative", "Normal"),
            ("Minimum and Maximum Boundary Values", "Boundary"),
            ("Empty and Single-Element Inputs", "Empty/Single"),
            ("Duplicate Values and Repeated Characters", "Duplicates"),
            ("Negative Numbers, Zero, and Positive Numbers", "Negative"),
            ("Large Inputs for Performance Testing", "Large"),
            ("Special Characters, Whitespace, and Case Variations", "Special"),
            ("Meaningful Words and Phrases", "Normal"),
            ("Inputs Designed to Expose Bugs", "Boundary")
        ]

        case_idx = 1
        for cat_name, dom_key in category_map:
            # Generate 12-15 cases for this category
            for i in range(13):
                test_inp = {}
                for p in params:
                    domain_list = param_domains[p.name]
                    # Find matching domain values or fallback
                    matching = [v for k, v in domain_list if k == dom_key]
                    val_pool = matching[0] if matching else domain_list[0][1]
                    val = val_pool[i % len(val_pool)]
                    test_inp[p.name] = val

                is_bug = (cat_name == "Inputs Designed to Expose Bugs" or i == 0 and "Empty" in cat_name)
                cases.append({
                    "title": f"{cat_name} Case #{case_idx}",
                    "category": cat_name,
                    "inputs": test_inp,
                    "reason": f"Systematic combinatorial evaluation targeting {cat_name.lower()}.",
                    "is_bug_exposing": is_bug
                })
                case_idx += 1

        return cases

    @classmethod
    def _ensure_minimum_100_cases(
        cls,
        cases: List[Dict[str, Any]],
        analysis: CodeAnalysis,
        target_count: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Deduplicates inputs and guarantees that at least `target_count` unique,
        categorized test cases are present by systematically expanding variations.
        """
        seen: Set[str] = set()
        deduped = []
        for c in cases:
            sig = normalize_input_signature(c.get("inputs", {}))
            if sig not in seen:
                seen.add(sig)
                deduped.append(c)

        if len(deduped) >= target_count:
            return deduped

        # Systematically generate distinct variations until target_count is reached
        params = analysis.input_parameters
        param_names = [p.name for p in params] if params else ["input_val"]
        iteration = 1

        categories = [
            "Normal and Representative",
            "Minimum and Maximum Boundary Values",
            "Duplicate Values and Repeated Characters",
            "Negative Numbers, Zero, and Positive Numbers",
            "Inputs Designed to Expose Bugs",
            "Special Characters, Whitespace, and Case Variations",
            "Meaningful Words and Phrases"
        ]

        while len(deduped) < target_count and iteration < 500:
            cat = categories[iteration % len(categories)]
            new_input = {}
            for idx, p in enumerate(params):
                t = p.type_name.lower()
                if "int" in t:
                    new_input[p.name] = (iteration * 3) + idx
                elif "float" in t:
                    new_input[p.name] = round((iteration * 1.5) + idx, 2)
                elif "str" in t:
                    new_input[p.name] = f"test_val_{iteration}_{idx}"
                elif "list" in t or "[" in t:
                    new_input[p.name] = [iteration, iteration + 1, iteration + 2]
                elif "bool" in t:
                    new_input[p.name] = (iteration % 2 == 0)
                else:
                    new_input[p.name] = iteration

            sig = normalize_input_signature(new_input)
            if sig not in seen:
                seen.add(sig)
                deduped.append({
                    "title": f"Systematic Permutation {len(deduped) + 1}",
                    "category": cat,
                    "inputs": new_input,
                    "reason": f"Systematic parameter boundary variation {iteration}.",
                    "is_bug_exposing": False
                })
            iteration += 1

        return deduped

    @classmethod
    def generate_rule_based_cases(cls, analysis: CodeAnalysis, raw_code: str) -> List[Dict[str, Any]]:
        """Produces categorized, meaningful test cases tailored to the inferred problem logic."""
        import re
        func_clean = re.sub(r'[^a-z0-9]', '', analysis.function_name.lower())
        purpose_clean = re.sub(r'[^a-z0-9]', '', analysis.purpose.lower())
        code_clean = re.sub(r'[^a-z0-9]', '', raw_code.lower())

        # 1. ANAGRAM CHECKER
        if "anagram" in func_clean or "anagram" in purpose_clean or "anagram" in code_clean:
            return cls._get_anagram_cases()

        # 2. TWO SUM
        if "twosum" in func_clean or "twosum" in code_clean or ("sum" in func_clean and ("target" in code_clean or "nums" in code_clean)):
            return cls._get_twosum_cases()

        # 3. PALINDROME CHECKER
        if "palindrome" in func_clean or "palindrome" in purpose_clean or "palindrome" in code_clean:
            return cls._get_palindrome_cases()

        # 4. BINARY SEARCH
        if "binarysearch" in func_clean or "binarysearch" in code_clean or ("search" in func_clean and "target" in code_clean):
            return cls._get_binarysearch_cases()

        # 5. AVERAGE / MEAN
        if "average" in func_clean or "mean" in func_clean or ("average" in code_clean and "total" in code_clean):
            pname = analysis.input_parameters[0].name if analysis.input_parameters else "numbers"
            return cls._get_average_cases(pname)

        # 6. GENERIC SYNTHESIZED SUITE FOR ANY CUSTOM FUNCTION
        return cls._get_generic_synthesized_cases(analysis, target_count=105)

    @classmethod
    async def generate_test_cases(
        cls,
        analysis: CodeAnalysis,
        raw_code: str,
        api_key: Optional[str] = None,
        min_cases: int = 100
    ) -> List[TestCaseItem]:
        """
        Coordinates rule-based generation with optional LLM generation,
        deduplicates equivalent test cases, and establishes verified ground truth.
        Guarantees at least min_cases (default 100) test cases.
        """
        raw_cases = cls.generate_rule_based_cases(analysis, raw_code)

        # If Gemini API key is provided, enrich with LLM-generated targeted test cases
        effective_key = api_key or os.environ.get("GEMINI_API_KEY")
        if effective_key:
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=effective_key)
                llm_prompt = f"""
You are an expert test suite designer. Generate 10 additional HIGH-VALUE, LOGIC-BASED test cases for the program below.
Target specific edge cases, boundary conditions, or subtle logic defects.
DO NOT generate arbitrary random strings or nonsense. Use meaningful words or values.

Function: {analysis.signature}
Purpose: {analysis.purpose}
Identified potential bugs: {', '.join(analysis.potential_bugs)}

Source Code:
{raw_code}

Return a JSON array of objects with fields:
- "title": descriptive title
- "category": one of ("Normal and Representative", "Minimum and Maximum Boundary Values", "Empty and Single-Element Inputs", "Duplicate Values and Repeated Characters", "Negative Numbers, Zero, and Positive Numbers", "Special Characters, Whitespace, and Case Variations", "Meaningful Words and Phrases", "Inputs Designed to Expose Bugs", "Large Inputs for Performance Testing")
- "inputs": object with parameter name keys and appropriate input values
- "reason": specific explanation of why this test case was selected
- "is_bug_exposing": boolean
"""
                candidate_models = [
                    os.environ.get("GEMINI_MODEL", "").strip(),
                    "gemini-3.5-flash-lite",
                    "gemini-flash-lite-latest",
                    "gemini-3.8-flash"
                ]
                models_to_try = [m for i, m in enumerate(candidate_models) if m and m not in candidate_models[:i]]

                for model_name in models_to_try:
                    try:
                        resp = client.models.generate_content(
                            model=model_name,
                            contents=llm_prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.2
                            )
                        )
                        extra = json.loads(resp.text)
                        if isinstance(extra, list):
                            raw_cases.extend(extra)
                        break
                    except Exception as err:
                        logger.info(f"LLM test case generation failed on {model_name}: {err}. Trying next candidate...")
            except Exception as e:
                logger.warning(f"LLM test case generation setup failed: {e}")

        # Ensure deduplication and minimum target count (at least 100)
        deduped_cases = cls._ensure_minimum_100_cases(raw_cases, analysis, target_count=min_cases)

        # Build TestCaseItem objects and determine expected outputs via ReferenceOracle
        final_test_cases: List[TestCaseItem] = []
        for idx, item in enumerate(deduped_cases, 1):
            inputs = item.get("inputs", {})
            expected, verified = ReferenceOracle.get_expected_output(
                analysis,
                inputs,
                raw_code,
                api_key=None # Rule-based oracle evaluation for instant response
            )

            final_test_cases.append(TestCaseItem(
                id=idx,
                title=item.get("title", f"Test Case {idx}"),
                category=item.get("category", "Normal and Representative"),
                inputs=inputs,
                input_formatted=format_inputs(inputs),
                expected_output=expected,
                actual_output=None,
                status="UNVERIFIED",
                reason=item.get("reason", "Targeted boundary and logic verification."),
                execution_time_ms=None,
                error_message=None,
                is_bug_exposing=item.get("is_bug_exposing", False)
            ))

        return final_test_cases
