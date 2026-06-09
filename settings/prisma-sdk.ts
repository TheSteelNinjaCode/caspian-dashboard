import path, { resolve } from "path";
import { writeFileSync } from "fs";
import psdk from "@prisma/internals";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const { getDMMF, getConfig, getSchemaWithPath } = psdk;
const schemaPath: string = resolve(__dirname, "../prisma");
const prismaSchemaJsonPath: string = resolve(__dirname, "prisma-schema.json");

export const prismaSdk = async (): Promise<void> => {
  try {
    const schemaResult = await getSchemaWithPath({
      schemaPath: { cliProvidedPath: schemaPath },
    });
    const schemas = schemaResult.schemas.map(
      ([filePath, content]: [string, string]) => {
        const relativePath = path.relative(
          schemaResult.schemaRootDir,
          filePath,
        );
        const schemaFilePath = (relativePath || path.basename(filePath))
          .split(path.sep)
          .join("/");

        return [schemaFilePath, content] as [string, string];
      },
    );

    // 2. Parse the schema models (DMMF)
    const dmmf = await getDMMF({ datamodel: schemas });

    // 3. Parse the configuration (Datasources & Generators)
    const config = await getConfig({ datamodel: schemas });

    // 4. Merge them into one object
    const fullJson = {
      ...dmmf,
      datasources: config.datasources,
      generators: config.generators,
    };

    // Write the combined data to JSON
    writeFileSync(prismaSchemaJsonPath, JSON.stringify(fullJson, null, 2));
    console.log(
      `Schema (DMMF + Config) converted to JSON from ${schemas.length} file(s)!`,
    );
  } catch (error) {
    console.error("Error parsing schema:", error);
  }
};

if (process.argv[1] && process.argv[1].endsWith("prisma-sdk.ts")) {
  prismaSdk();
}
