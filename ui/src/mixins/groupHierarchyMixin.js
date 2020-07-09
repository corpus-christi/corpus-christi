import {
  Group,
  getAllSubNodes,
  Participant,
  count,
  getInfoTree,
  isRootNode
} from "../models/GroupHierarchyNode";

const groupHierarchyMixin = {
  data() {
    return {
      $_groupHierarchyMixin_groups: [],
      $_groupHierarchyMixin_persons: [],
      $_groupHierarchyMixin_loading: true
    };
  },
  mounted() {
    this.$_groupHierarchyMixin_fetch();
  },
  computed: {
    $_groupHierarchyMixin_groupMap() {
      // turn the array into a map
      return this.$data.$_groupHierarchyMixin_groups.reduce(
        (acc, cur) => ({ ...acc, [cur.id]: cur }),
        {}
      );
    },
    /* get a composite tree with root groups and persons, shown in admin view */
    $_groupHierarchyMixin_adminTree() {
      let counter = count();
      // get all root groups and root participants
      let rootNodes = [
        ...this.$data.$_groupHierarchyMixin_groups.map(
          groupObject =>
            new Group(groupObject, this.$_groupHierarchyMixin_groupMap)
        ),
        ...this.$data.$_groupHierarchyMixin_persons.map(
          person =>
            new Participant({ person }, this.$_groupHierarchyMixin_groupMap)
        )
      ].filter(node => isRootNode(node));
      const adminNode = { name: "Admin", children: [] };
      rootNodes.forEach(rootNode => {
        adminNode.children.push(getInfoTree(rootNode, false, counter));
      });
      console.log("adminNode", adminNode);
      return [adminNode];
    }
  },
  methods: {
    $_groupHierarchyMixin_fetch() {
      this.$_groupHierarchyMixin_loading = true;
      Promise.all([
        this.$http.get("api/v1/groups/groups"),
        this.$http.get("api/v1/people/persons")
      ]).then(([respGroup, respPeople]) => {
        console.log("Groups fetched from groupHierarchyMixin", respGroup.data);
        console.log("People fetched from groupHierarchyMixin", respPeople.data);
        this.$data.$_groupHierarchyMixin_groups = respGroup.data; // access $ _ started variables with $data
        this.$data.$_groupHierarchyMixin_persons = respPeople.data;
        this.$data.$_groupHierarchyMixin_loading = false;
      });
    },

    /* Functions below depend on the fetched groups; if used, should bind the result to 'computed' properties
     * or add conditional rendering (v-if) on '$data.$_groupHierarchyMixin_loading'
     * in the template to prevent rendering before the groups are fetched.
     * If need to call function directly, use waitUntil to resolve the value asynchronously */

    /* get all leading groups of (groups that are authorized to) a participant according to the leadership hierarchy */
    $_groupHierarchyMixin_leadingGroups(participant) {
      return getAllSubNodes(
        new Participant(participant, this.$_groupHierarchyMixin_groupMap)
      )
        .filter(hn => hn.nodeType === "Group")
        .map(hn => hn.getObject());
    },

    /* get a tree from the given person */
    $_groupHierarchyMixin_getTree(person) {
      let participant = new Participant(
        { person },
        this.$_groupHierarchyMixin_groupMap
      );
      return getInfoTree(participant);
    }
  }
};

export default groupHierarchyMixin;
