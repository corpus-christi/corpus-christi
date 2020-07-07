/* This file contains algorithms needed to resolve group hierarchy permissions */

/* API response objects mappers */
// The object nested in a person object, that indicates which group the participant belongs
export interface PersonParticipantObject {
  groupId: number;
}

// The object nested in a group object, that indicates which person the participant associates with
export interface GroupParticipantObject {
  person: PersonObject;
}

export interface PersonObject {
  id: number;
  managers: PersonParticipantObject[];
  members: PersonParticipantObject[];
}

export interface GroupObject {
  id: number;
  managers: GroupParticipantObject[];
  members: GroupParticipantObject[];
}

export type NodeObject =
  | GroupParticipantObject
  | PersonParticipantObject
  | GroupObject;

export interface GroupMap {
  [id: number]: GroupObject;
}

export abstract class HierarchyNode {
  constructor(public nodeType: string) {}
  abstract get id(): number | string;
  abstract equal(other: HierarchyNode): boolean;
  abstract getObject(): NodeObject;
  abstract getSubNodes(): HierarchyNode[];
  abstract getSuperNodes(): HierarchyNode[];
}

export class Participant extends HierarchyNode {
  constructor(
    protected participant: GroupParticipantObject,
    protected groupMap: GroupMap
  ) {
    super("Participant");
  }
  get id(): number {
    return this.participant.person.id;
  }
  toString(): string {
    return `Participant(personId=${this.participant.person.id})`;
  }
  getObject(): NodeObject {
    return this.participant;
  }
  getLeadingGroups(): Group[] {
    return this.participant.person.managers.map(
      (m: PersonParticipantObject) =>
        new Group(this.groupMap[m.groupId], this.groupMap)
    );
  }
  getParticipatingGroups(): Group[] {
    return this.participant.person.members.map(
      (m: PersonParticipantObject) =>
        new Group(this.groupMap[m.groupId], this.groupMap)
    );
  }
  getSubNodes(): HierarchyNode[] {
    return this.getLeadingGroups();
  }
  getSuperNodes(): HierarchyNode[] {
    return this.getParticipatingGroups();
  }
  equal(other: HierarchyNode): boolean {
    if (other instanceof Participant) {
      return this.id === other.id;
    }
    return false;
  }
}

export class Group extends HierarchyNode {
  constructor(protected group: GroupObject, protected groupMap: GroupMap) {
    super("Group");
  }
  get id(): number {
    return this.group.id;
  }
  toString(): string {
    return `Group(id=${this.group.id})`;
  }
  getObject(): NodeObject {
    return this.group;
  }
  getMembers(): Participant[] {
    return this.group.members.map(
      (participant: GroupParticipantObject) =>
        new Participant(participant, this.groupMap)
    );
  }
  getManagers(): Participant[] {
    return this.group.managers.map(
      (participant: GroupParticipantObject) =>
        new Participant(participant, this.groupMap)
    );
  }
  getSubNodes(): HierarchyNode[] {
    return this.getMembers();
  }
  getSuperNodes(): HierarchyNode[] {
    return this.getManagers();
  }
  equal(other: HierarchyNode): boolean {
    if (other instanceof Group) {
      return this.id === other.id;
    }
    return false;
  }
}

/* wraps a HierarchyNode, enabling a graph representation */
export class GraphNode {
  // a 'cache' of nodes along the parent path
  private _parentPath: GraphNode[] = [];
  private _children: GraphNode[] = [];
  private _parentNode: GraphNode | null = null;
  private addChild(childNode: GraphNode) {
    this._children.push(childNode);
  }
  constructor(
    public hierarchyNode: HierarchyNode,
    parentNode: GraphNode | null = null,
    public id: string = ""
  ) {
    this.parentNode = parentNode;
  }
  get parentPath() {
    return [...this._parentPath];
  }
  get children() {
    return [...this._children];
  }
  get parentNode(): GraphNode | null {
    return this._parentNode;
  }
  set parentNode(parentNode: GraphNode | null) {
    if (this._parentNode !== null) {
      throw new Error(
        "Can't set parent node when the parent node is already set"
      );
    }
    this._parentNode = parentNode;
    if (this._parentNode !== null) {
      this._parentPath = [this._parentNode, ...this._parentNode.parentPath];
      this._parentNode.addChild(this);
    }
  }
}

/* Depth first search.
 * takes an initial node and performs a depth first search
 * parameters:
 * 1. node: the initial node to perform the search
 * 2. getAdjacentNodes: a callback that is called on each node encountered
 * should return a list of HierarchyNode that is adjacent to 'currentNode'
 * the callback also receives an optional second parameter 'parentPath'
 * which is an array representing the path all the way to the root node
 * the last element in the array is the root node.
 * 3. transform (optional): an optional filter to transform each of the GraphNode created
 * This can be useful to create custom id on each of the node.
 * Due to the order of traversal, each node passed to the callback (except the rootnode)
 * will have its 'parentNode' set, but not necessarily its children
 * returns:
 * a tree structure represented by a single root GraphNode */
export function dfs(
  node: HierarchyNode,
  getAdjacentNodes: (
    currentNode: HierarchyNode,
    parentPath: HierarchyNode[]
  ) => HierarchyNode[],
  transform: (node: GraphNode) => GraphNode = node => node
): GraphNode {
  const stack: GraphNode[] = [];
  const rootNode: GraphNode = transform(new GraphNode(node));
  let currentNode: GraphNode;

  stack.push(rootNode);
  while (stack.length > 0) {
    currentNode = stack.pop()!;
    let pendingNodes: HierarchyNode[] = getAdjacentNodes(
      currentNode.hierarchyNode,
      currentNode.parentPath.map(graphNode => graphNode.hierarchyNode)
    );
    for (let pendingNode of pendingNodes) {
      stack.push(transform(new GraphNode(pendingNode, currentNode)));
    }
  }
  return rootNode;
}

/* return a list of distinct sub-nodes, including the current node
 * from a given HierarchyNode
 * 'minDepth' and 'maxDepth' specify a range of distance from the root node
 * within which the nodes are to be included in the returned list
 * for both 'minDepth' and 'maxDepth,' a value of 0 disables the depth filter
 * if 'superNodes' is set, returns super-nodes instead; */
export function getAllSubNodes(
  node: HierarchyNode,
  minDepth: number = 0,
  maxDepth: number = 0,
  superNodes: boolean = false
): HierarchyNode[] {
  const allSubNodes: HierarchyNode[] = [];
  const adj = (node: HierarchyNode) =>
    node[superNodes ? "getSuperNodes" : "getSubNodes"]();
  dfs(node, (currentNode, parentPath) => {
    if (allSubNodes.some(node => currentNode.equal(node))) {
      // if current node is already in collection, stop searching
      return [];
    }
    if (minDepth && parentPath.length < minDepth) {
      // if less than minDepth, keep searching but don't collect current node
      return adj(currentNode);
    }
    if (maxDepth && parentPath.length === maxDepth) {
      // if reached maxDepth, collect current node and stop searching
      allSubNodes.push(currentNode);
      return [];
    }
    allSubNodes.push(currentNode);
    return adj(currentNode);
  });
  return allSubNodes;
}

/* a generator to generate unique positive integers */
function* count(start = 0, step = 1) {
  let i = start;
  while (true) {
    yield i;
    i += step;
  }
}

/* error object containing information about a (unexpected) cycle in the tree */
export class HierarchyCycleError extends Error {
  constructor(message: string, public node: GraphNode) {
    super(message);
    this.name = "HierarchyCycleError";
  }
}

/* returns a tree that can be used to render a treeview component.
 * namely, each node will contain a unique id */
export function getTree(
  node: HierarchyNode,
  superNodes: boolean = false
): GraphNode {
  let counter = count();
  const rootNode = dfs(
    node,
    (node: HierarchyNode, parentPath: HierarchyNode[]) => {
      if (parentPath.length >= 2 && parentPath[1].equal(node)) {
        return []; // prevent infinite loop from immediate cycle caused by manager-member double identity
      }
      return node[superNodes ? "getSuperNodes" : "getSubNodes"]();
    },
    graphNode => {
      if (
        graphNode.parentPath
          .slice(2) // ignore the immediate parent to allow someone to be both manager/member of a group
          .some(parentNode =>
            parentNode.hierarchyNode.equal(graphNode.hierarchyNode)
          )
      ) {
        throw new HierarchyCycleError("Unexpected cycle in tree", graphNode);
      }
      let next = counter.next();
      if (next.done) {
        throw new Error("counter running out of elements");
      }
      graphNode.id = next.value.toString();
      return graphNode;
    }
  );
  return rootNode;
}

/* checks whether a group is a root group
 * a root group is a group that has sub-groups
 * but does not have any super-group */
export function isRootGroup(group: Group): boolean {
  return true;
}
