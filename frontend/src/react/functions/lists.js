export function splitList(list, n) {
  const lists = []; // Initialize empty list of lists
  for (let i = 0; i < n; i++) {
    lists.push([]); // Add empty list to lists
  }
  for (let i = 0; i < list.length; i++) {
    const listIndex = i % n; // Calculate index of list to add item to
    lists[listIndex].push(list[i]); // Add item to list
  }
  return lists;
}
