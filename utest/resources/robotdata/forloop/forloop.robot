*** Test Cases ***
Test 0
  FOR  ${i}  IN RANGE  1  10
      Log  joo
  END
  FOR  ${j}  IN  1  2
      Log  jee
      Log  another
      Log  and another
  END

Test 1
  No Operation

Test 2
  FOR  ${j}  IN  1  2
      One
    Two
      Three

Test 3
  FOR  ${j}  IN  1  2
    One
      Two
      Three

Test 4
  FOR  ${j}  IN  1  2
      One
      Two
    Three
  END

Test 5
  FOR  ${j}  IN  1  2
      One
  Two
      Three
  END

Test 6
  FOR  ${j}  IN  1  2
      One
      Two
      Three
  END

Test 7
  FOR  ${j}  IN  1  2
      One
      Two
    Three
  END

Test 8
  FOR  ${a}  IN RANGE  100
    Log  Moi
  END
  Foo

Test 9
  Log  Something

Test 10
  Nothing

Test 11
  Not For loop
    One
    Two
    Three

Test 12
  Foo

Test 13
  Log  something
  FOR  ${i}  IN  1  2
    Log  ${i}
  END

Test 14
  FOR  ${i}  IN  1  2
    No Operation
  END

Test 15
  FOR  ${kuu}  IN RANGE  100
    Kw1  # comment
    Keyword  # comment
  END

Test 16
  Foo

Test 17
  FOR  ${i}  IN  1  2  3  4
    No Operation
  END
  FOR  ${j}  IN RANGE  100
    Fail
  END

Test 18
  FOR  ${i}  IN  1  2  3  4
    No Operation
    No Operation
  FOR  ${j}  IN  1  2  3  4
  FOR  ${k}  IN  1  2  3  4
    No Operation
    No Operation

Test 19
  FOR  ${loop1}  IN RANGE  1  19
    No Operation
    FOR  ${loop2}  IN RANGE  ${loop1}  20
      No Operation
      FOR  ${loop3}  IN RANGE  2  4
        No Operation
        Log  This is loop 3: ${loop3}
        No Operation
      END
      No Operation
      Log  This is loop 2: ${loop2}
    END
    Log  This is loop 1: ${loop1}
    No Operation
    Log  Generic
  END
