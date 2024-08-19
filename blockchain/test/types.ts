import { ContractTransactionResponse } from "ethers";

export type DeployableTransaction = {
  deploymentTransaction(): ContractTransactionResponse;
};
