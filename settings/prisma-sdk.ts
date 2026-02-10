import path, { resolve } from "path";
import { readFileSync, writeFileSync } from "fs";
import psdk from "@prisma/internals";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const { getDMMF, getConfig } = psdk;
const schemaPath: string = resolve(__dirname, "../prisma/schema.prisma");
const prismaSchemaJsonPath: string = resolve(__dirname, "prisma-schema.json");

export const prismaSdk = async (): Promise<void> => {
  try {
    const schema = readFileSync(schemaPath, "utf-8");

    // 2. Parse the schema models (DMMF)
    const dmmf = await getDMMF({ datamodel: schema });

    // 3. Parse the configuration (Datasources & Generators)
    const config = await getConfig({ datamodel: schema });

    // 4. Merge them into one object
    const fullJson = {
      ...dmmf,
      datasources: config.datasources,
      generators: config.generators,
    };

    // Write the combined data to JSON
    writeFileSync(prismaSchemaJsonPath, JSON.stringify(fullJson, null, 2));
    console.log("Schema (DMMF + Config) converted to JSON!");
  } catch (error) {
    console.error("Error parsing schema:", error);
  }
};

if (process.argv[1] && process.argv[1].endsWith("prisma-sdk.ts")) {
  prismaSdk();
}
