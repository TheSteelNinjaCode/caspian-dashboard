import { PrismaClient } from "@prisma/client";
import { PrismaBetterSqlite3 } from "@prisma/adapter-better-sqlite3";

const adapter = new PrismaBetterSqlite3({
  url: process.env.DATABASE_URL!,
});
const prisma = new PrismaClient({ adapter });

// ============================================================
// 2. DATA DEFINITION
// ============================================================

const userRoleData = [
  { id: 1, name: "Admin" },
  { id: 2, name: "User" },
];

const userData = [
  {
    name: "Juan",
    email: "j@gmail.com",
    password:
      "scrypt:32768:8:1$MmggiPD6tw2gvjHr$a7adb38c13b2dcbbd72b078b65b1db046777bf6f07c4db6cd7850bba1ef39d1fce74b3cb284fcf013953cffe3e72f67651e9a4393e81855ecd36cfd16404ff7b", // temp: 123
    roleId: 1,
  },
];

// ============================================================
// 3. EXECUTION LOGIC
// ============================================================

async function main() {
  console.log(`Start seeding ...`);

  await prisma.user.deleteMany();
  await prisma.userRole.deleteMany();
  await prisma.userRole.createMany({ data: userRoleData });
  await prisma.user.createMany({ data: userData });

  console.log(`Seeding finished.`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
