import {
  getAllSubNodes,
  HierarchyNode,
  GraphNode,
  Group,
  GroupMap,
  Participant,
  PersonObject,
  getTree
} from "../../src/models/GroupHierarchyNode";

interface PersonMap {
  [id: number]: PersonObject;
}

declare global {
  namespace jest {
    interface Matchers<R> {
      toContainHierarchyNode(other: HierarchyNode): R;
    }
  }
}

expect.extend({
  toContainHierarchyNode(array: HierarchyNode[], other: HierarchyNode) {
    let index: number = array.findIndex(node => node.equal(other));
    let pass: boolean, message: () => string;
    if (index === -1) {
      // not found
      pass = false;
      message = () =>
        `There is no hierarchyNode ${other.toString()} in collection ${array.toString()}`;
    } else {
      pass = true;
      message = () =>
        `HierarchyNode ${
          other.toString
        } found at index ${index} in collection ${array.toString()}`;
    }
    return { pass, message };
  }
});

describe("Test case 1", () => {
  let groupMap: GroupMap, personMap: PersonMap;
  beforeAll(() => {
    let groupMembers = [
      [1, 1],
      [1, 3],
      [1, 4],
      [2, 2],
      [2, 5],
      [3, 6],
      [3, 2],
      [4, 2],
      [9, 9]
    ];
    let groupManagers = [[1, 1], [2, 1], [3, 1], [4, 6], [9, 8]];
    ({ groupMap, personMap } = getMap(groupMembers, groupManagers));
  });

  test("hierarchy node subNodes and superNodes functionality", () => {
    let participantObject = {
      personId: 1,
      groupId: 1,
      person: personMap[1]
    };
    let participant = new Participant(participantObject, groupMap);
    expect(participant.getSubNodes().length).toBe(3);
    expect(participant.getSuperNodes().length).toBe(1);
  });

  test("getAllSubNodes depth filtering", () => {
    let subNodes;
    let participantObject = {
      personId: 1,
      groupId: 1,
      person: personMap[1]
    };
    let participant = new Participant(participantObject, groupMap);
    // get those only with depth 1
    subNodes = getAllSubNodes(participant, 1, 1);
    expect(subNodes.length).toBe(3);

    let g9: HierarchyNode = new Group(groupMap[9], groupMap);
    let p1: HierarchyNode = new Participant({ person: personMap[1] }, groupMap);
    // get from depth 1 to depth 2
    subNodes = getAllSubNodes(participant, 1, 2);
    expect(subNodes.length).toBe(9);
    expect(subNodes).not.toContainHierarchyNode(g9);
    expect(subNodes).toContainHierarchyNode(p1);

    // no range
    subNodes = getAllSubNodes(participant);
    expect(subNodes.length).toBe(10);
    expect(subNodes).not.toContainHierarchyNode(g9);
    expect(subNodes).toContainHierarchyNode(p1);
  });

  test("getTree functionality", () => {
    let rootNode;

    // get a tree branching down from Group 3
    rootNode = getTree(new Group(groupMap[3], groupMap));
    expect(rootNode.children.length).toBe(2);
    let p6: HierarchyNode = new Participant({ person: personMap[6] }, groupMap);
    let gnp6: GraphNode | undefined = rootNode.children.find(graphNode =>
      graphNode.hierarchyNode.equal(p6)
    ); // short for: graph node with person 6
    expect(gnp6).not.toBeUndefined();
    expect(gnp6!.children.length).toBe(1);
    let g4: HierarchyNode = new Group(groupMap[4], groupMap);
    let gng4 = gnp6!.children[0];
    expect(gng4.hierarchyNode.equal(g4)).toBe(true);
    expect(gng4.parentPath.length).toBe(2);
  });

  test("getTree cycle handling", () => {
    let rootNode: GraphNode;
    // get a tree branching down from Person 1
    rootNode = getTree(new Participant({ person: personMap[1] }, groupMap));
    expect(rootNode.children.length).toBe(3);
    let gng1: GraphNode | undefined = rootNode.children.find(graphNode =>
      graphNode.hierarchyNode.equal(new Group(groupMap[1], groupMap))
    );
    // expect Group 1 to be in Person1's children
    expect(gng1).not.toBeUndefined();
    let gnp1: GraphNode | undefined = gng1!.children.find(graphNode =>
      graphNode.hierarchyNode.equal(
        new Participant({ person: personMap[1] }, groupMap)
      )
    );
    // expect Person 1 to be in Group1's children
    // (because Person 1 is both a manager and member of Group 1)
    expect(gnp1).not.toBeUndefined();
    // expect no more children in gnp1 to prevent infinite recursion
    expect(gnp1!.children.length).toBe(0);
  });
});

// return an object containing personMap and groupMap
// personMap: { 1: { id: 1, members: [], managers: [{groupId: 1, personId: 1}] } }
// groupMap: { 1: { id: 1, members: [{ groupId: 1, personId: 2, person: {...} }, ...], managers: [...] } }
function getMap(groupMembers: number[][], groupManagers: number[][]) {
  const groupMap: GroupMap = {};
  const personMap: PersonMap = {};
  groupMembers.concat(groupManagers).forEach(([groupId, personId]) => {
    // create groups
    if (!Object.prototype.hasOwnProperty.call(groupMap, groupId)) {
      groupMap[groupId] = { id: groupId, members: [], managers: [] };
    }
    // create persons
    if (!Object.prototype.hasOwnProperty.call(personMap, personId)) {
      personMap[personId] = { id: personId, members: [], managers: [] };
    }
  });

  groupMembers.forEach(([groupId, personId]) => {
    groupMap[groupId].members.push({
      person: personMap[personId]
    });
    personMap[personId].members.push({ groupId });
  });

  groupManagers.forEach(([groupId, personId]) => {
    groupMap[groupId].managers.push({
      person: personMap[personId]
    });
    personMap[personId].managers.push({ groupId });
  });

  return { groupMap, personMap };
}
