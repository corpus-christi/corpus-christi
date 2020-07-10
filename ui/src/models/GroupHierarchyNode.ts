/* This file contains algorithms needed to resolve group hierarchy permissions */
import { intersectionWith } from "lodash";

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
  firstName?: string;
  lastName?: string;
}

export interface GroupObject {
  id: number;
  managers: GroupParticipantObject[];
  members: GroupParticipantObject[];
  name?: string;
}

export type NodeObject =
  | GroupParticipantObject
  | PersonParticipantObject
  | GroupObject;

export interface GroupMap {
  [id: number]: GroupObject;
}

/* turn a list of groups to a group map */
export function convertGroupMap(groupList: GroupObject[]) {
  return groupList.reduce((acc, cur) => ({ ...acc, [cur.id]: cur }), {});
}

export abstract class HierarchyNode {
  constructor(public nodeType: string) {}
  abstract get id(): number | string;
  abstract toString(): string;
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
      (m: PersonParticipantObject) => {
        if (!Object.prototype.hasOwnProperty.call(this.groupMap, m.groupId)) {
          throw new Error(
            `Cannot get leading group with id ${
              m.groupId
            } on participant with id ${
              this.id
            }: group does not exist in group map`
          );
        }
        return new Group(this.groupMap[m.groupId], this.groupMap);
      }
    );
  }
  getParticipatingGroups(): Group[] {
    return this.participant.person.members.map((m: PersonParticipantObject) => {
      if (!Object.prototype.hasOwnProperty.call(this.groupMap, m.groupId)) {
        throw new Error(
          `Cannot get participating group with id ${
            m.groupId
          } on participant with id ${
            this.id
          }: group does not exist in group map`
        );
      }
      return new Group(this.groupMap[m.groupId], this.groupMap);
    });
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

/* A tree node */
export interface TreeNode {
  name?: string;
  id?: string | number;
  children: TreeNode[];
}

/* like Array.prototype.map, returns a new tree,
 * where each node is transformed using 'mapFunc'
 * and 'addChild' is called to add each childNode to the parentNode */
export function mapTree<
  TIn extends TreeNode = GraphNode,
  TOut extends TreeNode = TreeNode
>(
  node: TIn,
  mapFunc: (node: TIn) => TOut,
  addChild: (parentNode: TOut, childNode: TOut) => void = (
    parentNode,
    childNode
  ) => {
    parentNode.children.push(childNode);
  }
): TOut {
  let mappedNode: TOut = mapFunc(node);
  node.children.forEach(child => {
    // 'child as TIn' assumes children are of the same subtype as the parent
    let childNode: TOut = mapTree(child as TIn, mapFunc, addChild);
    addChild(mappedNode, childNode);
  });
  return mappedNode;
}

/* A tree node class. wraps a HierarchyNode,
 * enabling a graph representation,
 * also provides useful attributes like parentPath */
export class GraphNode implements TreeNode {
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
    public id: string = "",
    public name: string = ""
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
 * returns:
 * a tree structure represented by a single root GraphNode */
export function dfs(
  node: HierarchyNode,
  getAdjacentNodes: (
    currentNode: HierarchyNode,
    parentPath: HierarchyNode[]
  ) => HierarchyNode[]
): GraphNode {
  const stack: GraphNode[] = [];
  const rootNode: GraphNode = new GraphNode(node);
  let currentNode: GraphNode;

  stack.push(rootNode);
  while (stack.length > 0) {
    currentNode = stack.pop()!;
    let pendingNodes: HierarchyNode[] = getAdjacentNodes(
      currentNode.hierarchyNode,
      currentNode.parentPath.map(graphNode => graphNode.hierarchyNode)
    );
    for (let pendingNode of pendingNodes) {
      stack.push(new GraphNode(pendingNode, currentNode));
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
export function* count(
  start = 0,
  step = 1
): Generator<number, undefined, undefined> {
  let i = start;
  while (true) {
    yield i;
    i += step;
  }
}

/* error object containing information about a (unexpected) cycle in the tree */
export class HierarchyCycleError extends Error {
  constructor(message: string, public node: HierarchyNode) {
    super(message);
    this.name = "HierarchyCycleError";
  }
}

/* returns a tree that represents the leadership hierarchy structure, represented by a root GraphNode */
export function getTree(
  node: HierarchyNode,
  superNodes: boolean = false
): GraphNode {
  // build the tree, detecting cycle as needed
  const rootNode = dfs(
    node,
    (node: HierarchyNode, parentPath: HierarchyNode[]) => {
      if (parentPath.length === 2 && parentPath[1].equal(node)) {
        return []; // prevent infinite loop from immediate cycle caused by manager-member double identity
      }
      if (
        parentPath.length > 2 &&
        parentPath
          .slice(2) // ignore the immediate parent to allow someone to be both manager/member of a group
          .some(parentNode => parentNode.equal(node))
      ) {
        throw new HierarchyCycleError("Unexpected cycle in tree", node);
      }
      return node[superNodes ? "getSuperNodes" : "getSubNodes"]();
    }
  );
  return rootNode;
}

// a tree node that also contains the underlying object and its type
interface InfoTreeNode extends TreeNode {
  nodeType: string;
  info: NodeObject;
}

/* returns a tree that can be used to render a treeview component.
 * unlike GraphNode, the nodes in this tree does not have any cross references
 * also, each node will contain a unique 'id', an intuitive 'name',
 * the underlying 'info' object, and its 'nodeType' */
export function getInfoTree(
  node: HierarchyNode,
  superNodes: boolean = false,
  counter: Generator<number | string, undefined, undefined> = count()
): InfoTreeNode {
  // map the tree to get rid of cross references, add id and name to each node
  let infoRootNode = mapTree<GraphNode, InfoTreeNode>(
    getTree(node, superNodes),
    graphNode => {
      let next = counter.next();
      if (next.done) {
        throw new Error("counter running out of elements");
      }
      let id: string = next.value.toString();
      let { hierarchyNode } = graphNode;
      let { nodeType } = hierarchyNode;
      let info = hierarchyNode.getObject();
      let name: string;
      // set node's name
      if (nodeType === "Group") {
        name = (info as GroupObject).name!;
      } else if (nodeType === "Participant") {
        let { firstName, lastName } = (info as GroupParticipantObject).person;
        name = `${firstName} ${lastName}`;
      } else {
        name = hierarchyNode.toString();
      }
      return {
        id,
        name,
        info,
        nodeType,
        children: []
      };
    },
    (parentNode, childNode) => {
      parentNode.children.push(childNode);
    }
  );
  return infoRootNode;
}

/* checks whether a node is a root node
 * a root node <r> is a node that either:
 * 1. does not have any super-node, or
 * 2. for all its immediate super-node <s> such that <r> is the only super-node of <s>
 * except possibly itself at depth 2, caused by manager/member double identity */
export function isRootNode(node: HierarchyNode): boolean {
  let immediateSuperNodes = node.getSuperNodes();
  for (let immediateSuperNode of immediateSuperNodes) {
    let grandSuperNodes = immediateSuperNode.getSuperNodes();
    if (!(grandSuperNodes.length === 1 && grandSuperNodes[0].equal(node))) {
      return false;
    }
  }
  return true;
}

/* checks whether connecting parentNode and childNode will not result in a cycle in existing tree
 * the logic is to check whether there is any ancestor node of parentNode
 * that is also a descendent node of childNode.
 * The fact that some person can be both a manager/member of a group
 * cause the algorithm to ignore some of the closely connected nodes */
export function checkConnection(
  parentNode: HierarchyNode,
  childNode: HierarchyNode
): void {
  let distantAncestors: HierarchyNode[] = []; // super-nodes with depth 2 and more
  let allAncestors: HierarchyNode[] = []; // all super-nodes
  let distantDescendents: HierarchyNode[] = []; // sub-nodes with depth 2 and more
  let allDescendents: HierarchyNode[] = []; // all sub-nodes

  dfs(parentNode, (currentNode, parentPath) => {
    if (distantAncestors.some(node => node.equal(currentNode))) return [];
    allAncestors.push(currentNode);
    if (parentPath.length >= 2) {
      distantAncestors.push(currentNode);
    }
    return currentNode.getSuperNodes();
  });

  dfs(childNode, (currentNode, parentPath) => {
    if (distantDescendents.some(node => node.equal(currentNode))) return [];
    allDescendents.push(currentNode);
    if (parentPath.length >= 2) {
      distantDescendents.push(currentNode);
    }
    return currentNode.getSubNodes();
  });

  /* above equivalent to following, only requires less search */
  // distantAncestors = getAllSubNodes(parentNode, 2, 0, true);
  // allAncestors = getAllSubNodes(parentNode, 0, 0, true);
  // distantDescendents = getAllSubNodes(childNode, 2, 0, false);
  // allDescendents = getAllSubNodes(childNode, 0, 0, false);

  let equal = (a: HierarchyNode, b: HierarchyNode) => a.equal(b);
  let cycleNodes: HierarchyNode[];
  cycleNodes = [
    ...intersectionWith(distantAncestors, allDescendents, equal),
    ...intersectionWith(distantDescendents, allAncestors, equal)
  ];
  if (cycleNodes.length !== 0) {
    throw new HierarchyCycleError(
      `Connection of parent ${parentNode.toString()} with child ${childNode.toString()} will cause cycle on node ${cycleNodes[0].toString()}`,
      cycleNodes[0]
    );
  }
}

/* a wrapper for checkConnection that does not throw errors */
export function isConnectionOkay(
  parentNode: HierarchyNode,
  childNode: HierarchyNode
): boolean {
  try {
    checkConnection(parentNode, childNode);
  } catch (HierarchyCycleError) {
    return false;
  }
  return true;
}
