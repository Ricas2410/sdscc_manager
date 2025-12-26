

# **Attendance & Groups Modules — Functional Specification**

---

## **ATTENDANCE MODULE**

### **1. User Roles**

* **Branch Admin**

  * Takes attendance for members in their branch.
  * Views attendance history for their branch.
  * Views individual member attendance summaries.

* **General Mission Admin**

  * Full attendance access across all branches.
  * Views attendance history and individual records globally.

---

### **2. Attendance Page (Main Page)**

Used to take attendance for a specific branch.

#### **2.1. Display**

A table/grid listing all members in the branch. Each row shows:

* Member name
* Thumbnail image
* Attendance checkbox (present/absent)

No additional member details appear on the attendance page.

#### **2.2. Behavior**

* Admin ticks checkboxes to mark members present.
* Clicking “Submit” records attendance for the day.
* Duplicate attendance for the same day should be prevented unless intentionally editing.

---

### **3. Attendance History Page**

A button on the attendance page navigates to History.

#### **3.1. Features**

* Filter records by:

  * Date
  * Branch
  * Service type (optional)
* List of past attendance sessions.
* Clicking a session opens:

  * Members present
  * Members absent

---

### **4. Member Attendance Details**

Displayed within each member’s profile.

#### **4.1. Placement**

* As a tab (e.g., “Attendance”), or
* As a linked section/page.

#### **4.2. Information Shown**

* Attendance percentage
* Total attended
* Total missed
* List of dates present
* List of dates absent

---

### **5. Permissions**

* **Branch Admin** → restricted to their own branch.
* **General Admin** → full access across all branches.

---

### **6. Minimal Data Requirements**

GPT-5.1 can infer models, requiring only:

* Members belong to a branch.
* Attendance is recorded per date.
* Each attendance record includes:

  * Member
  * Date
  * Status (present/absent)

---

## **GROUPS MODULE**

### **1. User Roles**

* **Branch Admin**

  * Manage groups within their branch.
  * Add/remove members from groups.
  * View group details and membership.

* **General Mission Admin**

  * Full group management across all branches.

---

### **2. Purpose**

Groups represent ministry teams, departments, committees, or service units.
A member can belong to multiple groups.

---

### **3. Groups List Page**

#### **3.1. Display**

List of all groups for the branch (or all branches for general admin):

* Group name
* Short description (optional)
* Number of members
* “View group” button

#### **3.2. Actions**

* Create new group
* Search groups by name
* Filter by branch (general admin only)

---

### **4. Group Details Page**

#### **4.1. Display**

* Group name
* Description
* Branch
* Members list showing:

  * Member name
  * Thumbnail
  * “Remove from group” button

#### **4.2. Actions**

* Edit group info
* Add members
* Remove members

---

### **5. Add Members to Group**

#### **5.1. Display**

* Search box
* List of members not already in the group
  For each:

  * Member name
  * Thumbnail
  * Checkbox

#### **5.2. Action**

* “Add Selected Members” button

---

### **6. Member Profile Integration**

Inside each member’s profile, include a **Groups** section/tab showing:

* List of groups the member belongs to
* Each group name links to the group details page
* Admins can add/remove

---

### **7. Permissions**

* **Branch Admin** → manage groups only in their own branch.
* **General Admin** → manage groups in all branches.

---

### **8. Minimal Data Requirements**

Only the following concepts are required:

* Group belongs to a branch.
* Group has many members.
* Member can belong to multiple groups.
* Group includes:

  * Name
  * Description (optional)


