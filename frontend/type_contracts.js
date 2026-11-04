// @ts-check
// Compile-only checks: unused @ts-expect-error directives fail the type gate.
import {serializeCsv} from "./src/csv.js";
import {axisTicks, marksDomain} from "./src/mark-scales.js";

serializeCsv([{name: "revenue", title: "Revenue"}], [{revenue: 20}]);
marksDomain({scale: {domain: [0, 100]}}, {min: 0, max: 100});
// @ts-expect-error Column identifiers must be strings.
serializeCsv([{name: 12}], []);
// @ts-expect-error Tick domains must be numeric.
axisTicks("zero", 10);
// @ts-expect-error A scale domain has two endpoints.
marksDomain({scale: {domain: [0, 1, 2]}}, null);
