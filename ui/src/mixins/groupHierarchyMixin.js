import { getAllSubNodes, Participant } from "../models/GroupHierarchyNode";

const groupHierarchyMixin = groupsText => ({
  // groupsText is a property on the component where a list of groups is found
  data() {
    return {
      [groupsText]: []
    };
  },
  mounted() {
    // TODO: add logic to detect whether the property exists in the component, and disable fetch if so.
    // currently this would make the component fetch twice if the component
    // itself is also fetching a list of group in its mounted hook. <2020-07-03, David Deng> //
    this.$http.get("api/v1/groups/groups").then(resp => {
      console.log("Groups fetched from groupHierarchyMixin", resp.data);
      this[groupsText] = resp.data;
    });
  },
  computed: {
    groupMap() {
      // turn the array into a map
      return this[groupsText].reduce(
        (acc, cur) => ({ ...acc, [cur.id]: cur }),
        {}
      );
    }
  },
  methods: {
    getAllSubGroups(participant) {
      return getAllSubNodes(new Participant(participant, this.groupMap))
        .filter(hn => hn.nodeType === "Group")
        .map(hn => hn.getObject());
    }
  }
});

export default groupHierarchyMixin;
