// To represent the partial object returned by marshmallow
interface PartialParticipantObject {
  groupId: number;
  personId: number;
}

interface ParticipantObject extends PartialParticipantObject {
  person: PersonObject;
}

interface PersonObject {
  id: number;
  managers: PartialParticipantObject[];
  members: PartialParticipantObject[];
}

interface GroupObject {
  id: number;
  managers: ParticipantObject[];
  members: ParticipantObject[];
}

type NodeObject = PartialParticipantObject | GroupObject;

interface GroupMap {
  [id: number]: GroupObject;
}

export abstract class HierarchyNode {
  constructor(public nodeType: string) {}
  abstract equal(other: HierarchyNode): boolean;
  abstract getObject(): NodeObject;
  abstract getSubNodes(): HierarchyNode[];
  abstract getSuperNodes(): HierarchyNode[];
}

export class Participant extends HierarchyNode {
  constructor(
    protected participant: ParticipantObject,
    protected groupMap: GroupMap
  ) {
    super("Participant");
  }
  getObject(): NodeObject {
    return this.participant;
  }
  getLeadingGroups(): Group[] {
    return this.participant.person.managers.map(
      (m: PartialParticipantObject) =>
        new Group(this.groupMap[m.groupId], this.groupMap)
    );
  }
  getParticipatingGroups(): Group[] {
    return this.participant.person.members.map(
      (m: PartialParticipantObject) =>
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
      return this.participant.personId === other.participant.personId;
    }
    return false;
  }
}

export class Group extends HierarchyNode {
  constructor(protected group: GroupObject, protected groupMap: GroupMap) {
    super("Group");
  }
  getObject(): NodeObject {
    return this.group;
  }
  getMembers(): Participant[] {
    return this.group.members.map(
      (participant: ParticipantObject) =>
        new Participant(participant, this.groupMap)
    );
  }
  getManagers(): Participant[] {
    return this.group.managers.map(
      (participant: ParticipantObject) =>
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
      return this.group.id === other.group.id;
    }
    return false;
  }
}

/* a wrapper for HierarchyNode, enabling a graph representation */
export class GraphNode {
  // a 'cache' of nodes along the parent path
  private _parentPath: GraphNode[] = [];
  private _children: GraphNode[] = [];
  private _parentNode: GraphNode | null = null;
  private addChild(childNode: GraphNode) {
    this._children.push(childNode);
  }
  private setParentNode(parentNode: GraphNode) {}
  constructor(
    public hierarchyNode: HierarchyNode,
    parentNode: GraphNode | null = null
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
 * by calling getAdjacentNodes on each node encountered
 * the callback also receives an optional second parameter
 * which is an array representing the path all the way to the root node
 * the last element in the array is the root node.
 * returns a tree structure represented by a single root GraphNode */
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
      currentNode.parentPath.map(gn => gn.hierarchyNode)
    );
    for (let pendingNode of pendingNodes) {
      stack.push(new GraphNode(pendingNode, currentNode));
    }
  }
  return rootNode;
}

/* return a list of distinct sub-nodes
 * from a given HierarchyNode
 * if superNodes is set, returns super-nodes instead */
export function getAllSubNodes(
  node: HierarchyNode,
  superNodes: boolean = false
): HierarchyNode[] {
  const allSubNodes: HierarchyNode[] = [];
  dfs(node, currentNode => {
    if (allSubNodes.some(node => currentNode.equal(node))) {
      return [];
    }
    console.log("currentNode", currentNode);
    allSubNodes.push(currentNode);
    return currentNode[superNodes ? "getSuperNodes" : "getSubNodes"]();
  });
  return allSubNodes;
}

/* returns a tree that can be used to render a treeview component
 * in vuetify */
export function getTree(
  node: HierarchyNode,
  superNodes: boolean = false
): GraphNode | void {}
