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
  /* like Array.prototype.map, returns a new tree,
   * where each node is transformed using 'mapFunc'
   * and 'addChild' is called to add each childNode to the parentNode
   * calling with default parameters will result in a simplified tree
   * where each node has only 'id', 'name' and 'children' */
  public map(
    mapFunc: (gn: GraphNode) => TreeNode = ({ name, id }) => ({
      id,
      name,
      children: []
    }),
    addChild: (parentNode: TreeNode, childNode: TreeNode) => void = (
      parentNode,
      childNode
    ) => {
      parentNode.children.push(childNode);
    }
  ): TreeNode {
    let mappedNode: TreeNode = mapFunc(this);
    this.children.forEach(child => {
      let childNode: TreeNode = child.map(mapFunc, addChild);
      addChild(mappedNode, childNode);
    });
    return mappedNode;
  }
  /* a hacky way to get rid of additional attributes like _parentPath.
   * to recursively convert a GraphNode to a simple nested JSON object,
   * do JSON.parse(JSON.stringify(graphNode)) on the root node of a tree */
  public toJSON() {
    let { hierarchyNode, children, id, name } = this;
    return { hierarchyNode, children, id, name };
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
  constructor(message: string, public node: GraphNode) {
    super(message);
    this.name = "HierarchyCycleError";
  }
}

/* returns a tree that can be used to render a treeview component.
 * namely, each node will contain a unique id */
export function getTree(
  node: HierarchyNode,
  superNodes: boolean = false,
  counter: Generator<number | string, undefined, undefined> = count()
): GraphNode {
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
      graphNode.name = graphNode.hierarchyNode.toString();
      graphNode.id = next.value.toString();
      return graphNode;
    }
  );
  return rootNode;
}

/* checks whether a node is a root node
 * a root node is a node that does not have any super-node */
export function isRootNode(node: HierarchyNode): boolean {
  return getAllSubNodes(node, 1, 1, true).length === 0;
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
      new GraphNode(cycleNodes[0])
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
