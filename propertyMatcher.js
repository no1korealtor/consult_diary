// propertyMatcher.js
function findMatchingProperties(properties, clientCondition) {
  return properties.filter(prop => {
    return prop.type === clientCondition.type && prop.price <= clientCondition.maxPrice;
  });
}

module.exports = { findMatchingProperties };
