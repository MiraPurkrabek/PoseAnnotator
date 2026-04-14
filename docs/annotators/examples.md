# Examples And Common Mistakes

Use these examples as a quick quality guide while annotating or reviewing annotations.

## Correct Example

Front-facing example:

![Correct example](../images/correct.gif)

Back-facing example:

![Correct example facing away](../images/right_back.png)

## Wrong Nose Visibility

The nose may be present but not directly visible. Visibility should reflect that.

<p float="middle">
  <img src="../images/wrong_nose_visibility.png" width="300" />
  <img src="../images/wrong_nose_visibility_fixed.png" width="300" />
</p>

## Wrong Keypoint Placement

Keep each point on the correct joint and avoid shifting it onto a neighboring body part.

<p float="middle">
  <img src="../images/wrong_keypoint.png" width="300" />
  <img src="../images/wrong_keypoint_fixed.png" width="300" />
</p>

## Missing Limbs

Do not silently skip limbs that are still inferable from the person and the pose definition.

<p float="middle">
  <img src="../images/missing_limb.png" width="300" />
  <img src="../images/missing_limb_fixed.png" width="300" />
</p>

## Review Checklist

Before moving on, quickly verify:
- left and right sides are not swapped
- keypoints sit on the intended joints
- visibility matches what is actually visible
- no required limb is missing
