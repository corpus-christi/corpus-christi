# Group Module Leadership Hierarchy

This document explains how the leadership hierarchy in Group Module works.

# Concept

The main purpose of the leadership hierarchy is to support an arbitrary number
of levels of leadership.

In a nutshell, some existing group leaders can be grouped together in a new
group, and leaders of that new group will have privilege over both the new
group and groups under it.

# Terminology

By _Participant_, we mean either a _Group Member_ or a _Group Manager_ in the
Group Module

A _Node_, or _HierarchyNode_, is an abstract entity representing either a
_Participant_ or a _Group_. Every _Node_ has the following characteristics:

-   super-nodes
    -   For a _Group_, its super-nodes are its _Group Manager_ s.
    -   For a _Participant_, its super-nodes are _Group_ s where the
        participant is a _Group Manager_.
-   sub-nodes
    -   For a _Group_, its sub-nodes are its _Member_ s.
    -   For a _Participant_, its sub-nodes are _Group_ s where the
        participant is a _Member_.

In this document, both _super-node_ and _sub-node_ will often be preceded with
a modifier _immediate_ or _all_.

_Immediate_ super/sub-nodes have the same meaning as super/sub-nodes used
without the modifier, according to the above definition. Their synonyms also
include _parent-node_ and _child-node_.

By _all_ super/sub-nodes, we also include the nodes that are the
_super/sub-node_ s of the current _Node_ 's _super/sub-node_ s, and the
_super/sub-node_ s of those, etc.

A user `u` is a _Group Overseer_ of group `g` if and only if `g` is among `u`'s
_all sub-nodes_.  

A node `gp` is a _grandparent-node_ of `n`, if `gp` is the immediate super-node
of some `pn`, where `pn` is an immediate super-node of `n`.

The diagram below illustrates some of the key terminologies.

![Terminology-illustration](https://g.gravizo.com/svg?  
digraph G {
    edge [fontcolor=sienna];
    subgraph cluster_1 {
        G1;
        fontcolor=grey;
        color=grey;
        label="Parent-node of Person 1,\nGrandparent-node of Group 2 and Group 3.";
    }
    subgraph cluster_0 {
        G2; G3;
        fontcolor=grey;
        color=grey;
        label="Child-node of Person 1,\n Grandchild-node of Group 1";
        labelloc=b;
    }
    G1 -> P1 [label="has member"];
    P1 -> G2 [label="is manager of"];
    P1 -> G3;
    G1 [label="Group 1"; xlabel="Group Node"];
    G2 [label="Group 2"; xlabel="Group Node"];
    G3 [label="Group 3"];
    P1 [shape=rectangle; label="Person 1"; xlabel="Participant Node"];
})

# Features

## Permission Control (not implemented)

The leadership hierarchy is used to grant more granular permission to different
users based on their belonging groups.

Unlike the _Group Admin_ role, which acts on all groups, the leadership
hierarchy system identifies the _Group Overseer_ s for _every group_.

Permissions to perform various operations (e.g. remove a group member, take
attendance, etc.) are granted based on the _Group Overseer_ role of the user.

> Security note: For now, the group hierarchy algorithm is implemented using
> Typescript/Javascript, and the backend would not have access to the leadership
> hierarchy information. As a result, someone could theoretically make direct
> request to the API to bypass this privilege checking.

> It would be best to find a way to use the algorithm on both the front-end and
> the back-end, without implementing it twice

## Cycle Prevention

Currently, the `GroupParticipants` component checks and prevents the user from
performing the following actions if the action introduces a cycle in the
leadership hierarchy:

-   adding a participant
-   moving a participant to another group
-   reactivating an archived participant
-   reactivating an archived group (not implemented)

## Hierarchy Treeview

The hierarchy treeview is implemented in `GroupTreeViewHierarchy` component.

### Admin User 

When the admin user navigates to that page, a tree will be rendered.  Since it
is possible for two groups to be _detached_, several _root node_ s are
identified before the tree is drawn.

A _root node_ `r` is a node that either:

1.  does not have any super-node, or
1.  each of its immediate super-nodes `s` satisfies the constraint that `r` is
    the only super-node of `s`.

    In other words, all of `r`'s grandparent-node (if any) is itself.

After the _root node_ s are identified, the component starts building a tree
from each of those _root node_ s, based on their sub-nodes. Repeated nodes are
shown but not expanded.

### Group Leader

Not implemented

# Edge Cases

## Manager-member double identity

Since it is common for a group manager to also be a member of the same group,
the hierarchy system permits the following linkage to be made, where "Person 1"
is both a manager and a member of "Group 1." 

Thus, the following situations are allowed.

#### Allowed Case: double identity
![double-identity-case-1](https://g.gravizo.com/svg?  
digraph G {
    G1a [label=Group1; color=red];
    P1 [label=Person1; shape=rectangle];
    G1b [label=Group1; color=red];
    G1a -> P1;
    P1 -> G1b;
}) 


#### Allowed Case: logically equivalent to the previous case

![double-identity-case-2](https://g.gravizo.com/svg?
digraph G {
    P1a [label=Person1; color=red; shape=rectangle];
    G1 [label=Group1];
    P1b [label=Person1; color=red; shape=rectangle];
    P1a -> G1;
    G1 -> P1b;
})

#### Allowed Case: multiple people with double identity
![double-identity-case-3](https://g.gravizo.com/svg?
digraph G {
    P1a -> G2 -> P1b;
    P2a -> G2 -> P2b;
    P1a [label=Person1, shape=rectangle, color=red];
    P1b [label=Person1, shape=rectangle, color=red];
    P2a [label=Person2, shape=rectangle, color=blue];
    P2b [label=Person2, shape=rectangle, color=blue];
    G2 [label=Group2];
})

> For this case, the rendered tree will be similar to the illustration below,
> Note that "Group 2" is a _root node_ being appended under the "Admin" node,
> and the lower-level "Group 2" are no longer expanded

> ![double-identity-case-3-tree](https://g.gravizo.com/svg?
digraph G {
    Admin -> G2;
    G2 -> P1 -> G2P1;
    G2 -> P2 -> G2P2;
    Admin [shape=diamond];
    P1 [label=Person1, shape=rectangle, color=red];
    P2 [label=Person2, shape=rectangle, color=blue];
    G2 [label=Group2];
    G2P1 [label=Group2];
    G2P2 [label=Group2];
})

#### Disallowed Case: Repeated node through different nodes

![double-identity-case-4](https://g.gravizo.com/svg?
digraph G {
    G2a -> P1 -> G1 -> P2 -> G2b
    P1 [label=Person1, shape=rectangle, color=yellow];
    P2 [label=Person2, shape=rectangle, color=blue];
    G1 [label=Group1, color=green];
    G2a [label=Group2, color=red];
    G2b [label=Group2, color=red];
})

Note there is no _root node_ in this diagram, there is no way for the treeview
component to pick up any of the nodes and start building the tree.
