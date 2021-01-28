/**
 * @file
 * @name GroupHierarchyNode.ts
 * @exports ../../tests/unit/GroupHierarchyNode.spec.ts
 * @exports ../components/groups/GroupLineGraph.vue
 * @exports ../components/groups/GroupMeetingMember.vue
 * @exports ../components/groups/GroupMeetingVisitor.vue
 * @exports ../components/groups/GroupParticipants.vue
 * @exports ../components/groups/GroupTable.vue
 * @exports ../components/groups/meetings/GroupMeetings.vue
 * @exports ../components/groups/treeview/GroupTreeViewHierarchy.vue
 * @exports ../components/groups/treeview/GroupTreeView.vue
 *  This file contains algorithms needed to resolve group hierarchy permissions.
 */

/* API response objects mappers */
// The object nested in a person object, that indicates which group the participant belongs
export interface PersonParticipantObject {
  active?: boolean;
  groupId: number;
}

// The object nested in a group object, that indicates which person the participant associates with
export interface GroupParticipantObject {
  active?: boolean;
  person: PersonObject;
}

export interface PersonObject {
  id: number;
  managers: PersonParticipantObject[];
  members: PersonParticipantObject[];
  active?: boolean;
  firstName?: string;
  lastName?: string;
}

export interface GroupObject {
  id: number;
  managers: GroupParticipantObject[];
  members: GroupParticipantObject[];
  active?: boolean;
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
export function convertToGroupMap(groupList: GroupObject[]) {
  return groupList.reduce((acc, cur) => ({ ...acc, [cur.id]: cur }), {});
}

/* construct a valid Participant class object with associated managers and members */
export function getParticipantById(
  personId: number,
  groupMap: GroupMap
): Participant | undefined {
  let fullParticipantObject: GroupParticipantObject | undefined;
  for (const id in groupMap) {
    const group = groupMap[id];
    let participant: GroupParticipantObject | undefined;
    if (
      (participant = group.members
        .concat(group.managers)
        .find((p: GroupParticipantObject) => p.person.id === personId))
    ) {
      fullParticipantObject = participant;
      break;
    }
  }
  if (!fullParticipantObject) {
    return undefined;
  }
  return new Participant(fullParticipantObject, groupMap);
}

export abstract class HierarchyNode {
  protected constructor(public nodeType: string) {}
  abstract get id(): number | string;
  abstract toString(): string;
  toHumanReadable(): string {
    return this.toString();
  }
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
  toHumanReadable(): string {
    const { firstName, lastName } = this.participant.person;
    return `${firstName} ${lastName}`;
  }
  getObject(): GroupParticipantObject {
    return this.participant;
  }
  getLeadingGroups(
    filter: (m: PersonParticipantObject) => boolean = (m) => true
  ): Group[] {
    return this.participant.person.managers
      .filter(filter)
      .map((m: PersonParticipantObject) => {
        if (!Object.prototype.hasOwnProperty.call(this.groupMap, m.groupId)) {
          throw new Error(
            `Cannot get leading group with id ${m.groupId} on participant with id ${this.id}: group does not exist in group map`
          );
        }
        return new Group(this.groupMap[m.groupId], this.groupMap);
      });
  }
  getParticipatingGroups(
    filter: (m: PersonParticipantObject) => boolean = (m) => true
  ): Group[] {
    return this.participant.person.members
      .filter(filter)
      .map((m: PersonParticipantObject) => {
        if (!Object.prototype.hasOwnProperty.call(this.groupMap, m.groupId)) {
          throw new Error(
            `Cannot get participating group with id ${m.groupId} on participant with id ${this.id}: group does not exist in group map`
          );
        }
        return new Group(this.groupMap[m.groupId], this.groupMap);
      });
  }
  getSubNodes(): HierarchyNode[] {
    return this.getLeadingGroups(
      (m) =>
        !!(
          m.active && // get groups where the user is an active manager
          Object.prototype.hasOwnProperty.call(this.groupMap, m.groupId) &&
          this.groupMap[m.groupId].active
        ) // only get the active groups
    );
  }
  getSuperNodes(): HierarchyNode[] {
    return this.getParticipatingGroups(
      (m) =>
        !!(
          m.active && // get groups where the user is an active member
          Object.prototype.hasOwnProperty.call(this.groupMap, m.groupId) &&
          this.groupMap[m.groupId].active
        ) // only get the active groups
    );
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
    if (!Object.prototype.hasOwnProperty.call(groupMap, group.id)) {
      throw new Error(
        `Can't construct Group instance when id ${group.id} is not in GroupMap`
      );
    }
  }
  get id(): number {
    return this.group.id;
  }
  toString(): string {
    return `Group(id=${this.group.id})`;
  }
  toHumanReadable(): string {
    return this.group.name || this.toString();
  }
  getObject(): GroupObject {
    return this.group;
  }
  getMembers(
    filter: (m: GroupParticipantObject) => boolean = (m) => true
  ): Participant[] {
    return this.group.members
      .filter(filter) // only get the active members
      .map(
        (participant: GroupParticipantObject) =>
          new Participant(participant, this.groupMap)
      );
  }
  getManagers(
    filter: (m: GroupParticipantObject) => boolean = (m) => true
  ): Participant[] {
    return this.group.managers
      .filter(filter) // only get the active managers
      .map(
        (participant: GroupParticipantObject) =>
          new Participant(participant, this.groupMap)
      );
  }
  getSubNodes(): HierarchyNode[] {
    return this.getMembers((m) => !!m.active);
  }
  getSuperNodes(): HierarchyNode[] {
    return this.getManagers((m) => !!m.active);
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
  const mappedNode: TOut = mapFunc(node);
  node.children.forEach((child) => {
    // 'child as TIn' assumes children are of the same subtype as the parent
    const childNode: TOut = mapTree(child as TIn, mapFunc, addChild);
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
 *   should return a list of HierarchyNode that is adjacent to 'currentNode'
 *   callback parameters:
 *     'currentNode': the node whose adjacent node should be returned by the callback
 *     'parentPath': an array representing the path all the way to the root node
 *       the last element in the array is the root node.
 *     'currentGraphNode': a GraphNode representing the current node. Note that its
 *       'children' property is empty when the callback is invoked
 * returns:
 * a tree structure represented by a single root GraphNode */
export function dfs(
  node: HierarchyNode,
  getAdjacentNodes: (
    currentNode: HierarchyNode,
    parentPath: HierarchyNode[],
    currentGraphNode: GraphNode
  ) => HierarchyNode[]
): GraphNode {
  const stack: GraphNode[] = [];
  const rootNode: GraphNode = new GraphNode(node);
  let currentNode: GraphNode;

  stack.push(rootNode);
  while (stack.length > 0) {
    currentNode = stack.pop()!;
    const pendingNodes: HierarchyNode[] = getAdjacentNodes(
      currentNode.hierarchyNode,
      currentNode.parentPath.map((graphNode) => graphNode.hierarchyNode),
      currentNode
    );
    for (const pendingNode of pendingNodes) {
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
    if (allSubNodes.some((node) => currentNode.equal(node))) {
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

export function isOverseer(person: Participant, groupId: number) {
  return getAllSubGroups(person).some((group) => group.id === groupId);
}

export function getAllSubGroups(person: Participant) {
  return getAllSubNodes(person).filter((node) => node.nodeType === "Group");
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
  constructor(
    message: string,
    public node: HierarchyNode,
    public path: HierarchyNode[] = [],
    public flag: string = ""
  ) {
    super(message);
    this.name = "HierarchyCycleError";
  }
}

/* checks whether the given parentPath contains a cycle with respect to currentNode.
 * this function is intended to be called in dfs's callback function, to make sure
 * no cycle exists. Throws an exception with 'unexpected' flag when a cycle is found.
 */
export function checkCycle(
  currentNode: HierarchyNode,
  parentPath: HierarchyNode[]
) {
  let cyclingNodeIndex: number;
  if (
    parentPath.length > 2 &&
    (cyclingNodeIndex = parentPath
      .slice(2) // ignore the immediate parent to allow someone to be both manager/member of a group
      .findIndex((parentNode) => parentNode.equal(currentNode))) !== -1
  ) {
    throw new HierarchyCycleError(
      "Unexpected cycle in tree",
      currentNode,
      parentPath
        .slice(0, cyclingNodeIndex + 2 + 1)
        .reverse()
        .concat(currentNode),
      "unexpected"
    );
  }
}

/* returns a tree that represents the leadership hierarchy structure, represented by a root GraphNode */
export function getTree(
  node: HierarchyNode,
  superNodes: boolean = false
): GraphNode {
  // build the tree, detecting cycle as needed
  return dfs(node, (node: HierarchyNode, parentPath: HierarchyNode[]) => {
    checkCycle(node, parentPath);
    const parentNode: HierarchyNode | undefined = parentPath[0];
    return node[superNodes ? "getSuperNodes" : "getSubNodes"]().filter(
      (hn) => !(parentNode && parentNode.equal(hn))
    );
  });
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
  return mapTree<GraphNode, InfoTreeNode>(
    getTree(node, superNodes),
    (graphNode) => {
      const next = counter.next();
      if (next.done) {
        throw new Error("counter running out of elements");
      }
      const id: string = next.value.toString();
      const { hierarchyNode } = graphNode;
      const { nodeType } = hierarchyNode;
      const info = hierarchyNode.getObject();
      const name: string = hierarchyNode.toHumanReadable();
      return {
        id,
        name,
        info,
        nodeType,
        children: [],
      };
    },
    (parentNode, childNode) => {
      parentNode.children.push(childNode);
    }
  );
}

/* checks whether a node is a root node
 * a root node <r> is a node that either:
 *   does not have any super-node, or
 *   its every 'immediate super-node' is also its 'immediate sub-node'.
 */
export function isRootNode(node: HierarchyNode): boolean {
  const immediateSuperNodes = node.getSuperNodes();
  const immediateSubNodes = node.getSubNodes();
  for (const supernode of immediateSuperNodes) {
    if (!immediateSubNodes.some((subnode) => subnode.equal(supernode))) {
      return false;
    }
  }
  return true;
}

/* checks whether connecting parentNode and childNode will not result in a cycle in existing tree
 * the logic is to check whether there is any ancestor node of parentNode that is also a
 * descendent node of childNode.
 * Throws an exception, including the cycling node and path when the connection will cause cycle.
 * If the cycle will be created by connecting parentNode and childNode, the exception thrown will
 * contain a 'preventive' flag, indicating it is an expected cycle to be prevented;
 * on the other hand, if a cycle is found when traversing the existing tree, the exception thrown
 * will contain an 'unexpected' flag, signaling it is an unexpected behavior.
 * The fact that some person can be both a manager/member of a group
 * cause the algorithm to ignore some of the closely connected nodes */
export function checkConnection(
  parentNode: HierarchyNode,
  childNode: HierarchyNode
): void {
  const allSuperNodes: GraphNode[] = [];
  // get all super nodes of parentNode
  // if along the way, there is a node that:
  // 1. is equal to its grandparent, or
  // 2. is equal to childNode, and whose grandparent will be childNode when connection is made (have a parentPath length of 1)
  // stop expanding at that node, and don't collect the node itself.
  // collect all other nodes into allSuperNodes
  dfs(
    parentNode,
    (
      hierarchyNode: HierarchyNode,
      parentPath: HierarchyNode[],
      graphNode: GraphNode
    ) => {
      checkCycle(hierarchyNode, parentPath);
      // 1. is equal to its grandparent, or
      if (parentPath.length >= 2 && parentPath[1].equal(hierarchyNode)) {
        return [];
      }
      // 2. is equal to childNode, and whose grandparent will be childNode when connection is made (have a parentPath length of 1)
      if (parentPath.length === 1 && hierarchyNode.equal(childNode)) {
        return [];
      }
      // collect the node
      allSuperNodes.push(graphNode);
      return hierarchyNode.getSuperNodes();
    }
  );
  // traverse through all sub nodes of childNode, and for each <node-child> encountered,
  // if <node-child>:
  // 1. is equal to its grandparent, or
  // 2. is equal to parentNode, and whose grandparent will be parentNode when connection is made (have a parentPath length of 1)
  // stop expanding at that node, and go to the next node.
  // other wise, if there is a <node-parent> in allSuperNodes that is equal to <node-child>,
  // raise an error with that path, which represents the cycling path
  dfs(
    childNode,
    (
      hierarchyNode: HierarchyNode,
      parentPath: HierarchyNode[],
      graphNode: GraphNode
    ) => {
      checkCycle(hierarchyNode, parentPath);
      // 1. is equal to its grandparent, or
      if (parentPath.length >= 2 && parentPath[1].equal(hierarchyNode)) {
        return [];
      }
      // 2. is equal to parentNode, and whose grandparent will be parentNode when connection is made (have a parentPath length of 1)
      if (parentPath.length === 1 && hierarchyNode.equal(parentNode)) {
        return [];
      }
      // otherwise, if there is a <node-parent> in allSuperNodes that is equal to <node-child>
      let cycleNode: GraphNode | undefined;
      if (
        (cycleNode = allSuperNodes.find((superNode) =>
          superNode.hierarchyNode.equal(hierarchyNode)
        ))
      ) {
        const cyclePath: HierarchyNode[] = [
          cycleNode.hierarchyNode,
          ...cycleNode.parentPath.map((g) => g.hierarchyNode),
          ...parentPath.reverse(),
          hierarchyNode,
        ];
        throw new HierarchyCycleError(
          `Connection of parent ${parentNode.toString()} with child ${childNode.toString()} will cause cycle on node ${cycleNode.hierarchyNode.toString()} with path ${cyclePath.map(
            (h) => h.toString()
          )}`,
          cycleNode.hierarchyNode,
          cyclePath,
          "preventive"
        );
      }
      return hierarchyNode.getSubNodes();
    }
  );
}

/* a wrapper for checkConnection that does not throw errors */
export function isConnectionOkay(
  parentNode: HierarchyNode,
  childNode: HierarchyNode
): boolean {
  try {
    checkConnection(parentNode, childNode);
  } catch (err) {
    if (err instanceof HierarchyCycleError) {
      return false;
    } else {
      throw err;
    }
  }
  return true;
}
