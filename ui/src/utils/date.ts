import moment from "moment";

export function formatDate(str: string): string {
  return moment(String(str)).format("MM/DD/YYYY hh:mm");
}
