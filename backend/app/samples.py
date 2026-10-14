"""Predefined sample code snippets for demonstration and evaluation."""

SAMPLE_CODES = [
    {
        "id": "anagram_checker",
        "title": "Anagram Checker (Set Frequency Defect)",
        "language": "python",
        "description": "Checks if two strings are anagrams. Contains a bug where it only compares set of characters instead of character frequencies.",
        "code": '''def is_anagram(s: str, t: str) -> bool:
    """
    Checks whether string 't' is an anagram of string 's'.
    """
    if len(s) != len(t):
        return False
    # Bug: Checks unique characters instead of exact character frequency counts
    # This incorrectly accepts strings like "aab" and "abb"!
    return set(s) == set(t)
'''
    },
    {
        "id": "two_sum",
        "title": "Two Sum (Index Self-Pairing Defect)",
        "language": "python",
        "description": "Finds two indices that add up to target. Contains a bug where an element can be used twice.",
        "code": '''def two_sum(nums: list, target: int) -> list:
    """
    Given an array of integers nums and an integer target,
    return indices of the two numbers such that they add up to target.
    """
    lookup = {}
    for i, num in enumerate(nums):
        complement = target - num
        # Bug: Doesn't check if the complement is at the same index
        # or overwrites lookup before verifying
        lookup[num] = i
        if complement in lookup:
            return [lookup[complement], i]
    return []
'''
    },
    {
        "id": "palindrome_cleaner",
        "title": "Valid Palindrome (Special Characters / Case Defect)",
        "language": "python",
        "description": "Checks if a phrase is a palindrome. Fails on punctuation, spaces, and mixed case.",
        "code": '''def is_palindrome(s: str) -> bool:
    """
    Returns true if the string is a palindrome after converting all uppercase
    letters into lowercase letters and removing all non-alphanumeric characters.
    """
    # Bug: Direct comparison without filtering non-alphanumerics or lowering case
    return s == s[::-1]
'''
    },
    {
        "id": "binary_search",
        "title": "Binary Search (Single Element / Upper Bound Off-by-One)",
        "language": "python",
        "description": "Searches for target in a sorted list. Off-by-one boundary defect on single-element search.",
        "code": '''def binary_search(nums: list, target: int) -> int:
    """
    Searches for target in a sorted list of unique integers.
    Returns index if found, else -1.
    """
    left = 0
    right = len(nums) - 1
    # Bug: 'left < right' terminates before evaluating single-element subarrays
    while left < right:
        mid = (left + right) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
'''
    },
    {
        "id": "safe_average",
        "title": "Average Calculator (Zero Division on Empty Input)",
        "language": "python",
        "description": "Computes average of list of numbers. Fails with ZeroDivisionError on empty list.",
        "code": '''def calculate_average(numbers: list) -> float:
    """
    Calculates the arithmetic mean of a list of numbers.
    """
    # Bug: Missing check for empty list, causes ZeroDivisionError
    total = sum(numbers)
    return total / len(numbers)
'''
    },
    {
        "id": "anagram_cpp",
        "title": "Anagram Checker (C++)",
        "language": "cpp",
        "description": "C++ implementation of anagram checker.",
        "code": '''#include <iostream>
#include <string>
#include <unordered_map>

bool isAnagram(std::string s, std::string t) {
    if (s.length() != t.length()) return false;
    std::unordered_map<char, int> counts;
    for (char c : s) counts[c]++;
    for (char c : t) {
        if (counts.find(c) == counts.end() || counts[c] == 0) return false;
        counts[c]--;
    }
    return true;
}

int main() {
    std::cout << (isAnagram("listen", "silent") ? "true" : "false") << std::endl;
    return 0;
}
'''
    },
    {
        "id": "palindrome_java",
        "title": "Palindrome Checker (Java)",
        "language": "java",
        "description": "Java implementation of valid palindrome verification.",
        "code": '''public class PalindromeChecker {
    public static boolean isPalindrome(String s) {
        if (s == null) return false;
        int left = 0, right = s.length() - 1;
        while (left < right) {
            while (left < right && !Character.isLetterOrDigit(s.charAt(left))) left++;
            while (left < right && !Character.isLetterOrDigit(s.charAt(right))) right--;
            if (Character.toLowerCase(s.charAt(left)) != Character.toLowerCase(s.charAt(right))) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }

    public static void main(String[] args) {
        System.out.println(isPalindrome("A man, a plan, a canal: Panama"));
    }
}
'''
    },
    {
        "id": "two_sum_java",
        "title": "Two Sum (Java - Self-Pairing Defect)",
        "language": "java",
        "description": "Java Two Sum with a defect where elements can pair with themselves when target = 2 * element.",
        "code": '''import java.util.HashMap;
import java.util.Map;

public class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> map = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            // Bug: Puts the element into the map before verifying complement,
            // which incorrectly allows an element to pair with itself!
            map.put(nums[i], i);
            if (map.containsKey(complement)) {
                return new int[] { map.get(complement), i };
            }
        }
        return new int[] {};
    }
}
'''
    },
    {
        "id": "anagram_java",
        "title": "Anagram Checker (Java - Frequency Defect)",
        "language": "java",
        "description": "Java Anagram checker comparing Character Sets instead of frequency counts.",
        "code": '''import java.util.HashSet;
import java.util.Set;

public class Solution {
    public boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) {
            return false;
        }
        // Bug: Compares unique characters (Set) rather than exact frequencies
        // Incorrectly accepts strings like "aab" and "abb"
        Set<Character> setS = new HashSet<>();
        Set<Character> setT = new HashSet<>();
        for (int i = 0; i < s.length(); i++) {
            setS.add(s.charAt(i));
            setT.add(t.charAt(i));
        }
        return setS.equals(setT);
    }
}
'''
    },
    {
        "id": "binary_search_java",
        "title": "Binary Search (Java - Boundary Off-by-One Defect)",
        "language": "java",
        "description": "Java Binary Search with off-by-one condition terminating before checking single-element subarrays.",
        "code": '''public class Solution {
    public int binarySearch(int[] nums, int target) {
        int left = 0;
        int right = nums.length - 1;
        // Bug: 'left < right' terminates before evaluating single-element subarrays
        while (left < right) {
            int mid = left + (right - left) / 2;
            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}
'''
    }
]
